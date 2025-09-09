# 📁 backend/app/schemas/editor.py

from pydantic import BaseModel, Field, HttpUrl, model_validator
from typing import List, Annotated


class CutRequest(BaseModel):
    """Requisição para cortar um trecho específico de um vídeo."""

    start_time: Annotated[float, Field(ge=0, example=5.5, description="Tempo de início em segundos")]
    end_time: Annotated[float, Field(gt=0, example=12.0, description="Tempo de fim em segundos")]

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time deve ser menor que end_time")
        return self


class MultipleCutRequest(BaseModel):
    """Requisição para cortes múltiplos em um vídeo."""

    cuts: Annotated[List[CutRequest], Field(min_length=1, description="Lista de cortes a serem realizados")]


class CutResponse(BaseModel):
    """Resposta após o corte de vídeo com sucesso."""

    output_url: Annotated[HttpUrl, Field(example="https://cdn.elgn.ai/cortes/video123.mp4", description="URL do vídeo cortado")]
