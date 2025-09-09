import os
import json
import requests
import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from api.deps import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# ========== 🔧 CONFIGURAÇÕES GERAIS ==========
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/google-drive/callback")

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY", "")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET", "")
DROPBOX_REDIRECT_URI = os.getenv("DROPBOX_REDIRECT_URI", "http://localhost:8000/dropbox/callback")

ONEDRIVE_CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID", "")
ONEDRIVE_CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET", "")
ONEDRIVE_REDIRECT_URI = os.getenv("ONEDRIVE_REDIRECT_URI", "http://localhost:8000/onedrive/callback")

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
user_tokens = {}

# ========== 🌐 GOOGLE DRIVE ==========
google_flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [GOOGLE_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    scopes=GOOGLE_SCOPES
)

@router.get("/google-drive/login")
def google_drive_login():
    """🔐 Inicia login com Google Drive."""
    auth_url, _ = google_flow.authorization_url()
    return {"auth_url": auth_url}

@router.get("/google-drive/callback")
def google_drive_callback(code: str = Query(...)):
    try:
        google_flow.fetch_token(code=code)
        creds = google_flow.credentials
        user_tokens["google_drive"] = creds.token
        return {"message": "✅ Google Drive conectado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no Google Drive: {e}")

@router.get("/google-drive/list")
def list_google_drive_files():
    token = user_tokens.get("google_drive")
    if not token:
        raise HTTPException(status_code=401, detail="❌ Não autenticado no Google Drive.")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers)
    response.raise_for_status()
    return response.json()

# ========== 🧊 DROPBOX ==========
@router.get("/dropbox/login")
def dropbox_login():
    """🔐 Inicia login com Dropbox."""
    url = f"https://www.dropbox.com/oauth2/authorize?client_id={DROPBOX_APP_KEY}&response_type=code&redirect_uri={DROPBOX_REDIRECT_URI}"
    return {"auth_url": url}

@router.get("/dropbox/callback")
def dropbox_callback(code: str = Query(...)):
    try:
        response = requests.post("https://api.dropbox.com/oauth2/token", data={
            "code": code,
            "grant_type": "authorization_code",
            "client_id": DROPBOX_APP_KEY,
            "client_secret": DROPBOX_APP_SECRET,
            "redirect_uri": DROPBOX_REDIRECT_URI
        })
        response.raise_for_status()
        data = response.json()
        user_tokens["dropbox"] = data["access_token"]
        return {"message": "✅ Dropbox conectado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no Dropbox: {e}")

@router.get("/dropbox/list")
def list_dropbox_files():
    token = user_tokens.get("dropbox")
    if not token:
        raise HTTPException(status_code=401, detail="❌ Não autenticado no Dropbox.")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post("https://api.dropboxapi.com/2/files/list_folder", headers=headers, json={"path": ""})
    response.raise_for_status()
    return response.json()

# ========== ☁ ONEDRIVE ==========
@router.get("/onedrive/login")
def onedrive_login():
    """🔐 Inicia login com OneDrive."""
    url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={ONEDRIVE_CLIENT_ID}&response_type=code"
        f"&redirect_uri={ONEDRIVE_REDIRECT_URI}&scope=files.read offline_access"
    )
    return {"auth_url": url}

@router.get("/onedrive/callback")
def onedrive_callback(code: str = Query(...)):
    try:
        response = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data={
            "client_id": ONEDRIVE_CLIENT_ID,
            "client_secret": ONEDRIVE_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": ONEDRIVE_REDIRECT_URI
        })
        response.raise_for_status()
        token_data = response.json()
        user_tokens["onedrive"] = token_data["access_token"]
        return {"message": "✅ OneDrive conectado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no OneDrive: {e}")

@router.get("/onedrive/list")
def list_onedrive_files():
    token = user_tokens.get("onedrive")
    if not token:
        raise HTTPException(status_code=401, detail="❌ Não autenticado no OneDrive.")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://graph.microsoft.com/v1.0/me/drive/root/children", headers=headers)
    response.raise_for_status()
    return response.json()

# ========== 📥 DOWNLOAD LOCAL ==========
class DownloadRequest(BaseModel):
    url: str
    filename: str

@router.post("/download-to-local", tags=["Integrations"])
def download_to_local(
    req: DownloadRequest,
    current_user: User = Depends(get_current_user)
):
    """⬇️ Baixa um arquivo externo por URL e salva localmente."""
    try:
        output_dir = os.getenv("DOWNLOAD_DIR", "downloads")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, req.filename)

        response = requests.get(req.url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return {"message": f"✅ Arquivo salvo com sucesso em: {filepath}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar arquivo: {e}")
