from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_db
from app.utils.language import get_language
from app.api.v1.schemas.scientific_name import ScientificNameCreate, ScientificNameUpdate
from app.services.scientific_name import (
    create_scientific_name,
    get_all_scientific_names,
    get_scientific_name_by_code,
    update_scientific_name,
    delete_scientific_name
)

router = APIRouter()

# CREATE Article
@router.post("/create")
async def add_scientific_name(
    scientific_name_data: ScientificNameCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_scientific_name(scientific_name_data, db)

# GET All scientific_name
@router.get("")
async def list_scientific_names(
    db: AsyncSession = Depends(get_db)
):
    return await get_all_scientific_names(db)

# GET Article by Code with optional lang
@router.get("/{scientific_name_code}")
async def get_scientific_name(
    scientific_name_code: int,
    lang: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_scientific_name_by_code(scientific_name_code, lang, db)

# UPDATE scientific_name
@router.put("/{scientific_name_code}")
async def edit_scientific_name(
    scientific_name_code: int,
    update_data: ScientificNameUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_scientific_name(scientific_name_code, update_data, db)

# DELETE scientific_name
@router.delete("/{scientific_name_code}")
async def remove_scientific_name(
    scientific_name_code: int,
    db: AsyncSession = Depends(get_db)
):
    return await delete_scientific_name(scientific_name_code, db)
