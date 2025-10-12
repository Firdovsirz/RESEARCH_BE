from app.services.otp import *
from app.services.user import *
from app.db.session import get_db
from app.api.v1.schemas.otp import *
from app.api.v1.schemas.user import *
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required

router = APIRouter()

# User profile

@router.get("/{fin_kod}/profile")
async def user_profile_endpoint(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_profile(fin_kod, lang_code, db)

# Get all users and its details

@router.get("/all")
async def get_all_users_endpoint(
    lang_code: str = Depends(get_language),
    search: str = Query(None, description="Search term for users and research areas"),
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_users(lang_code, search, start, end, db)

# Update user data by (patch) ("/api/user/{fin_kod}/update")
# Only name, surname, father_name, email can be updatable

@router.patch("/{fin_kod}/update")
async def update_user_endpoint(
    fin_kod: str,
    update_data: UpdateUser,
    db: AsyncSession = Depends(get_db)
):
    return await update_user(fin_kod, update_data, db)

@router.post("/create")
async def create_user_endpoint(
    user_request: CreateUser,
    db: AsyncSession = Depends(get_db)
):
    return await create_user(user_request, db)