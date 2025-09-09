# 📁 app/utils/admin_bypass.py

ADMIN_EMAIL = "elgn@tech.com"

def is_admin_email(email: str) -> bool:
    return email.lower() == ADMIN_EMAIL
