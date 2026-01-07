from app.services.otp import *
from app.db.session import get_db
from app.api.v1.schemas.otp import *
from app.services.inter_coor import *
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.utils.api_key_checker import check_api_key
from app.api.v1.schemas.inter_coor import CreateInterCoor

router = APIRouter()

@router.post("/create")
async def inter_corp_create_endpoint(
    inter_coor_request: CreateInterCoor,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await create_inter_coor(inter_coor_request, db)

@router.get("/{fin_kod}")
async def get_inter_coor_by_fin_endpoint(
    fin_kod: str,
    api_key: str = Depends(check_api_key),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_inter_corp_by_fin(fin_kod, lang_code, db)