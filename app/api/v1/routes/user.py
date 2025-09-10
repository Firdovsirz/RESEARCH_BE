from app.services.otp import *
from app.services.user import *
from app.db.session import get_db
from app.api.v1.schemas.otp import *
from fastapi import APIRouter, Depends
from app.api.v1.schemas.user import UpdateUser
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required

router = APIRouter()

# Update user data by (patch) ("/api/user/{fin_kod}/update")
# Only name, surname, father_name, email can be updatable

@router.patch("/{fin_kod}/update")
async def update_user_endpoint(
    fin_kod: str,
    update_data: UpdateUser,
    db: AsyncSession = Depends(get_db)   
):
    return await update_user(fin_kod, update_data, db)