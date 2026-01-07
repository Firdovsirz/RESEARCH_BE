from app.services.bio import (
    create_bio,
    get_all_bios,
    get_bio_by_code,
    update_bio,
    delete_bio
)
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.api.v1.schemas.bio import BioCreate, BioUpdate

router = APIRouter()

# CREATE Bio
@router.post("/create")
async def add_bio(
    bio_data: BioCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await create_bio(bio_data, db)

# GET All Bios
@router.get("")
async def list_bios(
    db: AsyncSession = Depends(get_db)
):
    return await get_all_bios(db)

# GET Bio by Code with optional lang
@router.get("/{bio_code}")
async def get_bio(
    bio_code: str,
    lang: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_bio_by_code(bio_code, lang, db)

# UPDATE Bio
@router.put("/{bio_code}")
async def edit_bio(
    bio_code: str,
    update_data: BioUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await update_bio(bio_code, update_data, db)

# DELETE Bio
@router.delete("/{bio_code}")
async def remove_bio(
    bio_code: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await delete_bio(bio_code, db)
