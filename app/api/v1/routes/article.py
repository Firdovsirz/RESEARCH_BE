from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_db
from app.utils.language import get_language
from app.api.v1.schemas.article import ArticleCreate, ArticleUpdate
from app.services.article import (
    create_article,
    get_all_articles,
    get_article_by_code,
    update_article,
    delete_article,
    get_article_by_fin_kod
)

router = APIRouter()

# CREATE Article
@router.post("/create")
async def add_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_article(article_data, db)

# GET All Articles
@router.get("")
async def list_articles(
    db: AsyncSession = Depends(get_db)
):
    return await get_all_articles(db)

# Get articles by fin kod
@router.get("/fin/{fin_kod}")
async def get_articles_by_fin_kod_endpoint(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_article_by_fin_kod(fin_kod, lang_code, db)

# GET Article by Code with optional lang
@router.get("/{article_code}")
async def get_article(
    article_code: str,
    lang: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_article_by_code(article_code, lang, db)

# UPDATE Article
@router.put("/{article_code}")
async def edit_article(
    article_code: str,
    update_data: ArticleUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_article(article_code, update_data, db)

# DELETE Article
@router.delete("/{article_code}")
async def remove_article(
    article_code: str,
    db: AsyncSession = Depends(get_db)
):
    return await delete_article(article_code, db)
