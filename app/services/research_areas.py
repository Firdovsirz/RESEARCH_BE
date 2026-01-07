import json
import random
from datetime import datetime
from app.models.auth import Auth
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy import select, delete
from sqlalchemy.orm import subqueryload
from app.db.redis_client import get_redis
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.api.v1.schemas.research_area import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.research_areas import ResearchAreas
from app.utils.translator import translate_to_english
from app.models.translations.research_areas_translations import ResearchAreasTranslations

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

        # Refresh Redis cache for this fin_kod
        try:
            redis = await get_redis()
            for lang_code in ["az", "en"]:
                cache_key = f"area:{area_request.fin_kod}:{lang_code}"
                areas_query = await db.execute(
                    select(ResearchAreas)
                    .where(ResearchAreas.fin_kod == area_request.fin_kod)
                )
                areas = areas_query.scalars().all()

                areas_arr = []
                for area in areas:
                    area_translation_query = await db.execute(
                        select(ResearchAreasTranslations)
                        .where(
                            ResearchAreasTranslations.area_code == area.area_code,
                            ResearchAreasTranslations.lang_code == lang_code
                        )
                    )
                    translation = area_translation_query.scalar_one_or_none()
                    areas_arr.append({
                        "fin_kod": area.fin_kod,
                        "area": translation.area if translation else "",
                        "area_code": area.area_code
                    })

                await redis.set(cache_key, json.dumps(areas_arr), ex=3600)
        except Exception:
            pass  # Ignore Redis errors

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
        redis = await get_redis()
        cache_key = f"area:{fin_kod}:{lang_code}"

        cached_data = await redis.get(cache_key)
        if cached_data:
            print("CACHE HIT - research areas")
            return JSONResponse(
                content={
                    "status_code": 200,
                    "areas": json.loads(cached_data)
                },
                status_code=status.HTTP_200_OK
            )

        print("CACHE MISS - research areas")

        user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == fin_kod)
        )
        user = user_query.scalar_one_or_none()
        if not user:
            return JSONResponse(
                content={"status_code": 404, "message": "User not found."},
                status_code=status.HTTP_404_NOT_FOUND
            )

        areas_query = await db.execute(
            select(ResearchAreas)
            .where(ResearchAreas.fin_kod == fin_kod)
        )
        areas = areas_query.scalars().all()
        if not areas:
            return JSONResponse(
                content={"status_code": 204, "message": "No content"},
                status_code=status.HTTP_204_NO_CONTENT
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
                "area": area_translation.area,
                "area_code": area.area_code
            }
            areas_arr.append(area_obj)

        # 3️⃣ Save to Redis for 1 hour
        await redis.set(cache_key, json.dumps(areas_arr), ex=3600)

        return JSONResponse(
            content={"status_code": 200, "areas": areas_arr},
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_area(
    fin_kod: str,
    area_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Check if the area exists
        area_query = await db.execute(
            select(ResearchAreas)
            .where(
                ResearchAreas.fin_kod == fin_kod,
                ResearchAreas.area_code == area_code
            )
        )
        area = area_query.scalar_one_or_none()

        if not area:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Area not found."
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Delete translations directly
        await db.execute(
            delete(ResearchAreasTranslations)
            .where(ResearchAreasTranslations.area_code == area_code)
        )

        # Delete the main area
        await db.execute(
            delete(ResearchAreas)
            .where(
                ResearchAreas.fin_kod == fin_kod,
                ResearchAreas.area_code == area_code
            )
        )

        # Commit the transaction
        await db.commit()

        # Clear Redis cache if used
        try:
            redis = await get_redis()
            await redis.delete(f"area:{fin_kod}:az")
            await redis.delete(f"area:{fin_kod}:en")
        except Exception:
            pass  # Ignore Redis errors

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Area deleted successfully."
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def edit_area(
    area_code: str,
    area_request: CreateArea,
    db: AsyncSession = Depends(get_db)
):
    try:
        area_query = await db.execute(
            select(ResearchAreas)
            .where(
                ResearchAreas.fin_kod == area_request.fin_kod,
                ResearchAreas.area_code == area_code
            )
        )
        area = area_query.scalar_one_or_none()

        if not area:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Area not found."
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        for lang_code in ["az", "en"]:
            area_translation_query = await db.execute(
                select(ResearchAreasTranslations)
                .where(
                    ResearchAreasTranslations.area_code == area_code,
                    ResearchAreasTranslations.lang_code == lang_code
                )
            )
            translation = area_translation_query.scalar_one_or_none()
            if translation:
                if lang_code == "az":
                    translation.area = area_request.research_area
                else:
                    translation.area = translate_to_english(area_request.research_area)
                db.add(translation)

        await db.commit()

        try:
            redis = await get_redis()
            await redis.delete(f"area:{area_request.fin_kod}:az")
            await redis.delete(f"area:{area_request.fin_kod}:en")
        except Exception:
            pass

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Area updated successfully."
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )