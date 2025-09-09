# 📁 backend/app/database/lib/user_crud.py

from beanie import PydanticObjectId
from app.models.user import User
from typing import Optional


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    🔍 Busca um usuário pelo ID.
    """
    return await User.get(PydanticObjectId(user_id))


async def update_user_seo_credits(user_id: str, decrement: int = 1) -> bool:
    """
    ✏️ Atualiza (decrementa) os créditos de SEO de um usuário.
    Retorna True se a operação for bem-sucedida.
    """
    user = await get_user_by_id(user_id)
    if user and user.seo_credits >= decrement:
        user.seo_credits -= decrement
        await user.save()
        return True
    return False
