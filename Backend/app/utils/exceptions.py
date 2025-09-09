# 📁 app/utils/exceptions.py

from fastapi import HTTPException

# === 🚨 Utilitário genérico ===


def raise_error(status_code: int, detail: str):
    """Lança um erro HTTP com status e detalhe customizado."""
    raise HTTPException(status_code=status_code, detail=detail)


# === 🔒 Autenticação ===


class UnauthorizedError(HTTPException):
    """Erro 401: Token ausente ou inválido."""

    def __init__(self, detail="Token ausente ou inválido"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(HTTPException):
    """Erro 403: Acesso negado ao recurso."""

    def __init__(self, detail="Acesso negado"):
        super().__init__(status_code=403, detail=detail)


# === 💳 Plano ou pagamento ===


class PaymentRequiredError(HTTPException):
    """Erro 402: Assinatura inativa ou plano inválido."""

    def __init__(self, detail="Plano inválido ou assinatura inativa"):
        super().__init__(status_code=402, detail=detail)


# === 📂 S3 e arquivos ===


class FileUploadError(HTTPException):
    """Erro 500: Falha no envio de arquivo."""

    def __init__(self, detail="Erro ao enviar arquivo para o S3"):
        super().__init__(status_code=500, detail=detail)


class FileDeleteError(HTTPException):
    """Erro 500: Falha ao remover arquivo."""

    def __init__(self, detail="Erro ao deletar arquivo do S3"):
        super().__init__(status_code=500, detail=detail)


# === 📈 Limite de uso ===


class RateLimitExceeded(HTTPException):
    """Erro 429: Limite de requisições excedido."""

    def __init__(
        self,
        detail="Limite de requisições excedido. "
        "Tente novamente mais tarde.",
    ):
        super().__init__(status_code=429, detail=detail)


# === 🧼 Validação de entrada ===


class BadRequestError(HTTPException):
    """Erro 400: Requisição inválida."""

    def __init__(self, detail="Requisição inválida"):
        super().__init__(status_code=400, detail=detail)


# === 🌐 Exportação controlada ===

__all__ = [
    "raise_error",
    "UnauthorizedError",
    "ForbiddenError",
    "PaymentRequiredError",
    "FileUploadError",
    "FileDeleteError",
    "RateLimitExceeded",
    "BadRequestError",
]
