from typing import Annotated
from app.services.auth import *
from fastapi import Path, Request
from app.db.session import get_db
from app.api.v1.schemas.auth import *
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required

router = APIRouter()

# Sign Up endpoint calling singup service ("/auth/singup")
# SignUp schema

@router.post("/signup")
async def singup_endpoint(
    signup_request: SignUp,
    db: AsyncSession = Depends(get_db)
):
    return await signup(signup_request, db)

# Sign In endpoint calling signin service ("/auth/singin")
# SignIn schema

@router.post("/signin")
async def signin_endpoint(
    signin_request: SignIn,
    db: AsyncSession = Depends(get_db)
):
    return await signin(signin_request, db)

# Reset Password endpoint calling reset_password ("/auth/reset-password")
# ResetPassword schema

@router.post("/reset-password")
async def reset_password_endpoint(
    reset_request: ResetPassword,
    db: AsyncSession = Depends(get_db)
):
    return await reset_password(reset_request, db)

@router.post("/translate")
async def translate_endpoint(
    text: str,
):
    return await translate(text)