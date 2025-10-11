import random
from app.models.research_areas import ResearchAreas
from datetime import datetime
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status
from sqlalchemy import select, delete
from app.models.scientific_name import ScientificName
from sqlalchemy.orm import subqueryload
from fastapi.responses import JSONResponse
from app.models.auth import Auth
from app.models.translations.research_areas_translations import ResearchAreasTranslations
from app.models.translations.scientific_name_translation import ScientificNameTranslation
from app.api.v1.schemas.research_area import *
from app.utils.translator import translate_to_english
from app.db.session import get_db

def generate_area_code() -> str:
    number = random.randint(0, 99999)
    return f"AREA-{number:05d}"

async def create_area(
    area_request: CreateArea,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == area_request.fin_kod)
        )

        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        area_code = generate_area_code()
        
        new_area = ResearchAreas(
            area_code = area_code,
            fin_kod = area_request.fin_kod,
            created_at = datetime.utcnow()
        )

        new_area_az = ResearchAreasTranslations(
            area_code = area_code,
            lang_code = "az",
            area = area_request.research_area
        )

        new_area_en = ResearchAreasTranslations(
            area_code = area_code,
            lang_code = "en",
            area = translate_to_english(area_request.research_area)
        )

        db.add(new_area)
        db.add(new_area_az)
        db.add(new_area_en)
        await db.commit()
        await db.refresh(new_area)
        await db.refresh(new_area_az)
        await db.refresh(new_area_en)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Research area created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_area_by_fin_code(
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
        
        areas_query = await db.execute(
            select(ResearchAreas)
            .where(ResearchAreas.fin_kod == fin_kod)
        )

        areas = areas_query.scalars().all()

        if not areas:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        areas_arr = []

        for area in areas:
            area_query = await db.execute(
                select(ResearchAreasTranslations)
                .where(
                    ResearchAreasTranslations.area_code == area.area_code,
                    ResearchAreasTranslations.lang_code == lang_code
                )
            )

            area_translation = area_query.scalar_one_or_none()

            area_obj = {
                "fin_kod": area.fin_kod,
                "area": area_translation.area
            }

            areas_arr.append(area_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "areas": areas_arr
            }, status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )