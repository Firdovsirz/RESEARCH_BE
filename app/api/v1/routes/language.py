from app.services.otp import *
from app.db.session import get_db
from app.services.language import *
from fastapi import APIRouter, Depends
from app.api.v1.schemas.language import *
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.utils.api_key_checker import check_api_key
from app.api.v1.schemas.inter_coor import CreateInterCoor

router = APIRouter()

@router.post("/create")
async def create_language_endpoint(
    language_request: CreateLanguage,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await add_language(language_request, db)

@router.get("/{fin_kod}")
async def get_languages_by_fin_kod_endpoint(
    fin_kod: str,
    api_key: str = Depends(check_api_key),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_languages_by_fin(fin_kod, lang_code, db)

@router.delete("/{lang_serial}/delete")
async def delete_lang_enpoint(
    lang_serial: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await delete_language(lang_serial, db)