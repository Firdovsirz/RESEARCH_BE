import random
from datetime import datetime
from app.models.auth import Auth
from app.models.work import Work
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.api.v1.schemas.work import *
from app.api.v1.schemas.language import *
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translations.work_translations import WorkTranslations
from app.models.translations.language_translations import LanguageTranslations

def generate_work_serial() -> str:
    number = random.randint(0, 99999)
    return f"WORK-{number:05d}"

async def add_work(
    work_request: CreateWork,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == work_request.fin_kod)
        )

        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        work_serial = generate_work_serial()
        
        new_work = Work(
            fin_kod=work_request.fin_kod,
            work_serial=work_serial,
            created_at=datetime.utcnow()
        )

        new_work_az = WorkTranslations(
            work_serial=work_serial,
            language_code="az",
            work_place=work_request.work_place,
            duty=work_request.duty,
            created_at=datetime.utcnow()
        )

        new_work_en = WorkTranslations(
            work_serial=work_serial,
            language_code="en",
            work_place=translate_to_english(work_request.work_place),
            duty=translate_to_english(work_request.duty),
            created_at=datetime.utcnow()
        )

        db.add(new_work)
        db.add(new_work_az)
        db.add(new_work_en)

        await db.commit()

        await db.refresh(new_work)
        await db.refresh(new_work_az)
        await db.refresh(new_work_en)

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

async def get_works_by_fin(
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
        
        works_arr = []

        works_query = await db.execute(
            select(Work)
            .where(Work.fin_kod == fin_kod)
        )

        works = works_query.scalars().all()

        if not works:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )

        for work in works:
            work_translation_query = await db.execute(
                select(WorkTranslations)
                .where(
                    WorkTranslations.work_serial == work.work_serial,
                    WorkTranslations.language_code == lang_code
                )
            )

            work_translation = work_translation_query.scalar_one_or_none()

            work_obj = {
                "work_place": work_translation.work_place,
                "duty": work_translation.duty
            }

            works_arr.append(work_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Works fetched successfully.",
                "works": works_arr
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )