# 📁 backend/app/main.py

from fastapi import FastAPI, HTTPException, Request, UploadFile, Depends, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app
from dotenv import load_dotenv
from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.prometheus import PrometheusMiddleware
from app.middleware.cors import add_cors_middleware
from app.api.router import api_router
from app.routes import health
from app.auth.dependencies import get_current_user
from app.api.payments.stripe_session import router as stripe_session_router
from app.api.payments.webhook import router as stripe_webhook_router
from app.api.zip.download import router as download_zip
from app.api import metrics
from app.models import Base  # 🔧 necessário para criar tabelas
from sqlalchemy import create_engine  # 🔧 engine manual
import openai
import os
import json
from uuid import uuid4
from typing import Optional, Annotated
from pydantic import BaseModel, constr
from app.auth.router import auth_router
from app.api import healthcheck
from app.api.feedback import router as feedback_router
from app.routes import storage
from app.routes import video_routes
from fastapi.staticfiles import StaticFiles

# === 🔐 ENV ===
load_dotenv()
openai.api_key = settings.openai_api_key

# === 🚀 FastAPI App ===
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# === 🧱 Criação do banco sem Alembic ===
@app.on_event("startup")
def on_startup():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    init_dirs()

# === 📂 Diretórios obrigatórios ===
def init_dirs():
    for path in [settings.UPLOAD_FOLDER, "radio_music", "static"]:
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretório {path}: {e}")

# === 🔗 Rotas principais ===
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(download_zip, prefix="/tools", tags=["Tools"])
app.include_router(health.router)
app.include_router(stripe_session_router)
app.include_router(stripe_webhook_router)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(healthcheck.router, prefix="/api/v1/status", tags=["Healthcheck"])
app.include_router(storage.router, prefix="/api/v1", tags=["Armazenamento"])
app.include_router(video_routes.router)

# === 📊 Prometheus ===
app.mount("/metrics", make_asgi_app())

# === 🎵 Estáticos (Rádio e Resultados) ===
app.mount("/radio/static", StaticFiles(directory="radio_music"), name="radio_music")
app.mount("/static", StaticFiles(directory="static"), name="static")

# === ⚙️ Middlewares Globais ===
app.add_middleware(GZipMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(PrometheusMiddleware)
add_cors_middleware(app)

# === 🩺 Health Check ===
@app.get("/api/v1/status/health")
async def status_health_check():
    return {"status": "ok", "app_name": settings.app_name}

# === 🔁 Temporário: Upload + Processamento IA ===
class EnhancementOptions(BaseModel):
    denoise: Optional[bool] = False
    stabilize: Optional[bool] = False

class SeoOptions(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[list[str]] = []

class UploadVideoInput(BaseModel):
    enhancements: EnhancementOptions
    seo: SeoOptions
    resolution: Annotated[str, constr(strip_whitespace=True)]
    aspectRatio: Annotated[str, constr(strip_whitespace=True)]

ALLOWED_EXTENSIONS = {"mp4", "mov", "webm"}
MAX_FILE_SIZE_MB = 200

@app.post("/api/process-video")
async def process_video(
    video: UploadFile,
    enhancements: str = Form(...),
    seo: str = Form(...),
    resolution: str = Form(...),
    aspectRatio: str = Form(...),
    current_user=Depends(get_current_user)
):
    try:
        ext = video.filename.split(".")[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

        contents = await video.read()
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(status_code=400, detail="Arquivo excede 200MB.")

        enhancements_data = json.loads(enhancements)
        seo_data = json.loads(seo)

        validated = UploadVideoInput(
            enhancements=enhancements_data,
            seo=seo_data,
            resolution=resolution,
            aspectRatio=aspectRatio
        )

        unique_filename = f"processed_{uuid4()}.{ext}"
        output_path = os.path.join("static", unique_filename)
        with open(output_path, "wb") as buffer:
            buffer.write(contents)

        return JSONResponse(
            content={
                "message": "✅ Processamento simulado com sucesso.",
                "video_url": f"/static/{unique_filename}"
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/generate-script")
async def generate_script(request: Request, current_user=Depends(get_current_user)):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        if not prompt:
            return JSONResponse({"error": "Prompt é obrigatório."}, status_code=400)

        completion = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em SEO e criação de conteúdo para vídeos."},
                {"role": "user", "content": prompt}
            ]
        )

        generated_text = completion.choices[0].message["content"].strip()
        return JSONResponse({"result": generated_text})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# === 🧱 Handler Global de Erros ===
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
