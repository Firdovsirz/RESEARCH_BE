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

# Verify otp
# Validate requested otp and save user records

@router.post("/signup/verify")
async def verify_signup_endpoint(
    otp_request: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db)
):
    return await verify_signup(otp_request, db)

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

# Approve user by admin ("/auth/{fin_kod}/approve")
# Update the approved column in auth to True

@router.post("/{fin_kod}/approve")
async def approve_user_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    return await approve_user(fin_kod, db)

# Reject user by admin ("/auth/{fin_kod}/reject")
# Delete user records from auth and user table

@router.post("/{fin_kod}/reject")
async def reject_user_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    return await reject_user(fin_kod, db)

# Get approve waiting approved
# Where Auth approve == 2

@router.get("/pending-users")
async def pending_users(
    db: AsyncSession = Depends(get_db)
):
    return await get_app_waiting_users(db)