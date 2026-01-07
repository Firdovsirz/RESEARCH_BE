from typing import Optional
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.services.research_areas import *
from app.utils.language import get_language
from app.api.v1.schemas.research_area import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.utils.api_key_checker import check_api_key

router = APIRouter()

@router.post("/create")
async def create_area_endpoint(
    area_request: CreateArea,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await create_area(area_request, db)

@router.get("/{fin_kod}")
async def get_research_area_by_fin_kod_endpoint(
    fin_kod: str,
    api_key: str = Depends(check_api_key),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_area_by_fin_code(fin_kod, lang_code, db)

@router.delete("/{fin_kod}/{area_code}/delete")
async def delete_area_endpoint(
    fin_kod: str,
    area_code: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await delete_area(fin_kod, area_code, db)

@router.put("/{area_code}/edit")
async def edit_area_endpoint(
    area_code: str,
    area_request: CreateArea,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await edit_area(area_code, area_request, db)