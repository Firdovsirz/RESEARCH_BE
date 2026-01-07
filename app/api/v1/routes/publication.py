from app.services.publication import (
    create_publication,
    get_all_publications,
    get_publication_by_code,
    update_publication,
    delete_publication
)
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.utils.api_key_checker import check_api_key
from app.api.v1.schemas.publication import PublicationCreate, PublicationUpdate

router = APIRouter()

# CREATE Publication
@router.post("/create")
async def add_publication(
    publication_data: PublicationCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await create_publication(publication_data, db)

# GET All Publications
@router.get("")
async def list_publications(
    db: AsyncSession = Depends(get_db)
):
    return await get_all_publications(db)

# GET Publication by Code with optional lang
@router.get("/{fin_kod}")
async def get_publication(
    fin_kod: str,
    api_key: str = Depends(check_api_key),
    lang: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_publication_by_code(fin_kod, lang, db)

# UPDATE Publication
@router.put("/{publication_code}/update")
async def edit_publication(
    publication_code: str,
    update_data: PublicationUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await update_publication(publication_code, update_data, db)

# DELETE Publication
@router.delete("/{publication_code}/delete")
async def remove_publication(
    publication_code: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await delete_publication(publication_code, db)
