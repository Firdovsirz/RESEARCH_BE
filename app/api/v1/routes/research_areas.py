from typing import Optional
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.services.research_areas import *
from app.utils.language import get_language
from app.api.v1.schemas.research_area import *
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/create")
async def create_area_endpoint(
    area_request: CreateArea,
    db: AsyncSession = Depends(get_db)
):
    return await create_area(area_request, db)

@router.get("/{fin_kod}")
async def get_research_area_by_fin_kod_endpoint(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_area_by_fin_code(fin_kod, lang_code, db)