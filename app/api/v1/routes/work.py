from app.services.otp import *
from app.services.work import *
from app.db.session import get_db
from app.api.v1.schemas.work import *
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.utils.api_key_checker import check_api_key

router = APIRouter()

@router.post("/create")
async def create_work_endpoint(
    work_request: CreateWork,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await add_work(work_request, db)

@router.get("/{fin_kod}")
async def get_works_by_fin_kod_endpoint(
    fin_kod: str,
    api_key: str = Depends(check_api_key),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_works_by_fin(fin_kod, lang_code, db)