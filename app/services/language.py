import random
from datetime import datetime
from app.models.auth import Auth
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.models.language import Language
from app.api.v1.schemas.language import *
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translations.language_translations import LanguageTranslations

def generate_lang_serial() -> str:
    number = random.randint(0, 99999)
    return f"LANG-{number:05d}"

async def add_language(
    language_request: CreateLanguage,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == language_request.fin_kod)
        )

        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        lang_serial = generate_lang_serial()
        
        new_language = Language(
            fin_kod=language_request.fin_kod,
            lang_serial=lang_serial,
            language_short_name=language_request.language_short_name,
            language_level=language_request.language_level,
            created_at=datetime.utcnow()
        )

        new_language_az = LanguageTranslations(
            fin_kod=language_request.fin_kod,
            lang_serial=lang_serial,
            lang_code="az",
            language_name=language_request.language_name,
            created_at=datetime.utcnow()
        )

        new_language_en = LanguageTranslations(
            fin_kod=language_request.fin_kod,
            lang_serial=lang_serial,
            lang_code="en",
            language_name=translate_to_english(language_request.language_name),
            created_at=datetime.utcnow()
        )

        db.add(new_language)
        db.add(new_language_az)
        db.add(new_language_en)

        await db.commit()

        await db.refresh(new_language)
        await db.refresh(new_language_az)
        await db.refresh(new_language_en)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Language details added successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_languages_by_fin(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == fin_kod)
        )

        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        langs_arr = []

        langs_query = await db.execute(
            select(Language)
            .where(Language.fin_kod == fin_kod)
        )

        langs = langs_query.scalars().all()

        if not langs:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )

        for lang in langs:
            lang_translation_query = await db.execute(
                select(LanguageTranslations)
                .where(
                    LanguageTranslations.lang_serial == lang.lang_serial,
                    LanguageTranslations.lang_code == lang_code
                )
            )

            lang_translation = lang_translation_query.scalar_one_or_none()

            language_obj = {
                "language_short_name": lang.language_short_name,
                "language_level": lang.language_level,
                "language_name": lang_translation.language_name
            }

            langs_arr.append(language_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Languages fetched successfully.",
                "languages": langs_arr
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )