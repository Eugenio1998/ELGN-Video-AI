from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ErrorType(str, Enum):
    """Tipos padronizados de erro retornados pela API."""
    VALIDATION = "validation_error"     # ❌ Erros de validação (formato, campos obrigatórios)
    AUTH = "auth_error"                 # 🔐 Erros de autenticação/autorização
    PROCESSING = "processing_error"     # ⚙️ Erros ao processar dados ou arquivos
    UNKNOWN = "unknown_error"           # ❓ Erros inesperados

class ErrorResponse(BaseModel):
    """
    Modelo padrão para respostas de erro na API.
    """
    detail: str = Field(..., description="Mensagem detalhada do erro.")
    status_code: Optional[int] = Field(None, description="Código HTTP relacionado ao erro.")
    error_type: Optional[ErrorType] = Field(ErrorType.UNKNOWN, description="Categoria do erro.")
    field: Optional[str] = Field(None, description="Campo que causou o erro (se aplicável).")
    hint: Optional[str] = Field(None, description="Dica opcional de como resolver o erro.")
