import pytest
from app.api.error_response import ErrorResponse, ErrorType

def test_error_response_structure():
    erro = ErrorResponse(
        detail="Erro genérico",
        status_code=400,
        error_type=ErrorType.UNKNOWN
    )
    assert erro.detail == "Erro genérico"
    assert erro.status_code == 400
    assert erro.error_type == ErrorType.UNKNOWN