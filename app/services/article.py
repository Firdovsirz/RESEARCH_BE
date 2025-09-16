import asyncio
from datetime import datetime
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status
from sqlalchemy import select, delete
from app.models.article import Article
from sqlalchemy.orm import subqueryload
from fastapi.responses import JSONResponse
from app.models.auth import Auth
from app.models.article_translation import ArticleTranslation
from app.api.v1.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
)
from app.utils.translator import translate_to_english
from app.db.session import get_db

# CREATE Article
async def create_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        existing_article_result = await db.execute(
            select(Article).where(Article.article_code == article_data.article_code)
        )
        existing_article = existing_article_result.scalar_one_or_none()

        if existing_article:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": f"There is such an article!"
                },
                status_code=status.HTTP_409_CONFLICT
            )

        existing_user_result = await db.execute(
            select(Auth).where(Auth.fin_kod == article_data.fin_kod)
        )
        existing_user = existing_user_result.scalar_one_or_none()

        if not existing_user:
            return JSONResponse(
                content={
                    "status_code": 400,
                    "message": f"User with fin_kod '{article_data.fin_kod}' does not exist!"
                }, status_code=status.HTTP_400_BAD_REQUEST
            )


        new_article = Article(
            fin_kod=article_data.fin_kod,
            article_code=article_data.article_code,
            created_at=datetime.utcnow()
        )

        db.add(new_article)
        await db.commit()
        await db.refresh(new_article)

        # Create az translation
        az_translation = ArticleTranslation(
            article_code=new_article.article_code,
            lang_code="az",
            article_field=article_data.article_field,
            created_at=datetime.utcnow()
        )
        db.add(az_translation)

        # Create en translation
        en_text = await asyncio.to_thread(translate_to_english, article_data.article_field, "az")
        en_translation = ArticleTranslation(
            article_code=new_article.article_code,
            lang_code="en",
            article_field=en_text,
            created_at=datetime.utcnow()
        )
        db.add(en_translation)

        await db.commit()
        await db.refresh(new_article)
        await db.refresh(az_translation)
        await db.refresh(en_translation)

        query = select(Article).where(Article.article_code == new_article.article_code).options(subqueryload(Article.translations))
        
        result = await db.execute(query)
        created_article = result.scalar_one_or_none()

        translations = []
        if created_article and created_article.translations:
            for translation in created_article.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "article_field": translation.article_field
                })

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Article created successfully!",
                "data": {
                    "id": created_article.id,
                    "fin_kod": created_article.fin_kod,
                    "article_code": created_article.article_code,
                    "translations": translations,
                    "created_at": created_article.created_at.isoformat() if created_article.created_at else None
                }
            }, status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_article_by_fin_kod(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        fin_kod_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == fin_kod)
        )

        user = fin_kod_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Fin kod is not valid."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        article_query = await db.execute(
            select(Article)
            .where(Article.fin_kod == fin_kod)
        )

        articles = article_query.scalars().all()

        if not articles:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        article_arr = []

        for article in articles:
            translation_query = await db.execute(
                select(ArticleTranslation)
                .where(
                    ArticleTranslation.article_code == article.article_code,
                    ArticleTranslation.lang_code == lang_code
                )
            )

            article_translation = translation_query.scalar_one_or_none()

            article_obj = {
                "article_field": article_translation.article_field
            }

            article_arr.append(article_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Articles fetched successfully.",
                "articles": article_arr
            }
        )
     
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# GET All Articles
async def get_all_articles(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        result = await db.execute(
            select(Article).options(subqueryload(Article.translations))
        )
        articles = result.unique().scalars().all()

        articles_data = []
        for article in articles:
            translations = []
            if article.translations:
                for translation in article.translations:
                    translations.append({
                        "lang_code": translation.lang_code,
                        "article_field": translation.article_field
                    })

            articles_data.append({
                "id": article.id,
                "fin_kod": article.fin_kod,
                "article_code": article.article_code,
                "translations": translations,
                "created_at": article.created_at.isoformat() if article.created_at else None
            })
        
        if articles_data == []:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "Data not found!",
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        else:
            return JSONResponse(
                content={
                    "status_code": 200,
                    "message": "Articles retrieved successfully!",
                    "data": articles_data
                }, status_code=status.HTTP_200_OK
            )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# GET Article by code with specific language
async def get_article_by_code(
    article_code: str,
    lang: str,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        article_result = await db.execute(
            select(Article).where(Article.article_code == article_code)
        )
        article = article_result.scalar_one_or_none()

        if not article:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Article not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        translation_result = await db.execute(
            select(ArticleTranslation).where(
                ArticleTranslation.article_code == article_code,
                ArticleTranslation.lang_code == lang
            )
        )
        translation = translation_result.scalar_one_or_none()

        if not translation:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": f"No translation found for language '{lang}'!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Article retrieved successfully!",
                "data": {
                    "id": article.id,
                    "fin_kod": article.fin_kod,
                    "article_code": article.article_code,
                    "article_field": translation.article_field,
                    "lang_code": translation.lang_code,
                    "created_at": article.created_at.isoformat() if article.created_at else None
                }
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# UPDATE Article
async def update_article(
    article_code: str,
    update_data: ArticleUpdate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        article_result = await db.execute(
            select(Article).where(Article.article_code == article_code)
        )
        article = article_result.scalar_one_or_none()

        if not article:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Article not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        # Update az translation
        az_translation_result = await db.execute(
            select(ArticleTranslation).where(
                ArticleTranslation.article_code == article_code,
                ArticleTranslation.lang_code == "az"
            )
        )
        az_translation = az_translation_result.scalar_one_or_none()
        
        if az_translation:
            az_translation.article_field = update_data.article_field
            az_translation.updated_at = datetime.utcnow()

        # Update en translation
        en_translation_result = await db.execute(
            select(ArticleTranslation).where(
                ArticleTranslation.article_code == article_code,
                ArticleTranslation.lang_code == "en"
            )
        )
        en_translation = en_translation_result.scalar_one_or_none()

        if en_translation:
            en_text = await asyncio.to_thread(translate_to_english, update_data.article_field, "az")
            en_translation.article_field = en_text
            en_translation.updated_at = datetime.utcnow()

        article.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(article)
        if az_translation:
            await db.refresh(az_translation)
        if en_translation:
            await db.refresh(en_translation)

        query = select(Article).where(
            Article.article_code == article_code
        ).options(subqueryload(Article.translations))
        
        result = await db.execute(query)
        updated_article = result.scalar_one_or_none()

        translations = []
        if updated_article and updated_article.translations:
            for translation in updated_article.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "article_field": translation.article_field
                })

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Article updated successfully",
                "data": {
                    "id": updated_article.id,
                    "fin_kod": updated_article.fin_kod,
                    "article_code": updated_article.article_code,
                    "translations": translations,
                    "created_at": updated_article.created_at.isoformat() if updated_article.created_at else None,
                    "updated_at": updated_article.updated_at.isoformat() if updated_article.updated_at else None
                }
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# DELETE Article
async def delete_article(
    article_code: str,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        article_result = await db.execute(
            select(Article).where(Article.article_code == article_code)
        )
        article = article_result.scalar_one_or_none()

        if not article:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Article not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        await db.execute(delete(ArticleTranslation).where(ArticleTranslation.article_code == article_code))
        await db.execute(delete(Article).where(Article.article_code == article_code))
        await db.commit()

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Article deleted successfully!"
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )