"""
Teste de importação e estrutura para o serviço: email_report_sender
"""

def test_import_email_report_sender():
    try:
        import app.services.email_report_sender as module
        assert module is not None
    except Exception as e:
        assert False, f"Erro ao importar email_report_sender: {e}"
