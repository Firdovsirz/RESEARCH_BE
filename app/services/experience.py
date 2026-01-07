import json
import random
from datetime import datetime
from app.db.database import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.db.redis_client import get_redis
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.experience import Experience
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.api.v1.schemas.experience import CreateExperience
from app.models.experience_translation import ExperienceTranslations


def generate_exp_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7))


async def add_experience(
    experience_request: CreateExperience,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        exp_code = generate_exp_code()

        new_experience = Experience(
            exp_code=exp_code,
            fin_kod=experience_request.fin_kod,
            start_date=experience_request.start_date,
            end_date=experience_request.end_date,
            created_at=datetime.utcnow()
        )

        new_translation_az = ExperienceTranslations(
            exp_code=exp_code,
            lang_code="az",
            title=experience_request.title,
            university=experience_request.university
        )

        new_translation = ExperienceTranslations(
            exp_code=exp_code,
            lang_code="en",
            title=translate_to_english(experience_request.title),
            university=translate_to_english(experience_request.university)
        )

        db.add(new_experience)
        db.add(new_translation_az)
        db.add(new_translation)
        await db.commit()
        await db.refresh(new_experience)
        await db.refresh(new_translation_az)
        await db.refresh(new_translation)

        # Refresh Redis cache for this user's experiences
        redis = await get_redis()
        keys = await redis.keys(f"experience:{experience_request.fin_kod}:*")
        for key in keys:
            await redis.delete(key)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "experience added successfully.",
                "exp_code": exp_code
            },
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_experience_by_code(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        redis = await get_redis()
        cache_key = f"experience:{fin_kod}:{lang_code}"

        cached_data = await redis.get(cache_key)
        if cached_data:
            print("CACHE HIT - experience")
            return JSONResponse(
                content={
                    "status_code": 200,
                    "message": "experience fetched successfully (from cache).",
                    "experiences": json.loads(cached_data)
                },
                status_code=status.HTTP_200_OK
            )

        print("CACHE MISS - experience")

        # 2️⃣ Fetch from DB
        result = await db.execute(
            select(Experience)
            .where(Experience.fin_kod == fin_kod)
            .order_by(Experience.start_date.desc())
        )
        experiences = result.scalars().all()

        if not experiences:
            return JSONResponse(
                content={"status_code": 204, "message": "NO CONTENT"},
                status_code=status.HTTP_204_NO_CONTENT
            )

        experience_arr = []
        for experience in experiences:
            translation_query = await db.execute(
                select(ExperienceTranslations).where(
                    ExperienceTranslations.exp_code == experience.exp_code,
                    ExperienceTranslations.lang_code == lang_code
                )
            )
            translation = translation_query.scalar_one_or_none()

            experience_obj = {
                "fin_kod": experience.fin_kod,
                "start_date": experience.start_date,
                "end_date": experience.end_date,
                "exp_code": experience.exp_code,
                "title": translation.title if translation else None,
                "university": translation.university if translation else None
            }
            experience_arr.append(experience_obj)

        # 3️⃣ Save to Redis for 1 hour
        await redis.set(cache_key, json.dumps(experience_arr), ex=3600)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "experience fetched successfully.",
                "experiences": experience_arr
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_all_experiences(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        result = await db.execute(select(Experience))
        experiences = result.scalars().all()

        if not experiences:
            return JSONResponse(
                content={"status_code": 204, "message": "No experiences found"},
                status_code=status.HTTP_204_NO_CONTENT
            )

        experiences_list = [
            {
                "exp_code": edu.exp_code,
                "start_date": edu.start_date,
                "end_date": edu.end_date,
                "created_at": edu.created_at.isoformat(),
                "updated_at": edu.updated_at.isoformat() if edu.updated_at else None
            }
            for edu in experiences
        ]

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "experiences fetched successfully.",
                "experiences": experiences_list
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_experience(
    exp_code: str,
    experience_request: CreateExperience,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        result = await db.execute(select(Experience).where(Experience.exp_code == exp_code))
        experience = result.scalar_one_or_none()

        if not experience:
            return JSONResponse(
                content={"status_code": 404, "message": "experience not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        experience.start_date = experience_request.start_date
        experience.end_date = experience_request.end_date
        experience.updated_at = datetime.utcnow()

        az_translation_query = await db.execute(
            select(ExperienceTranslations).where(
                ExperienceTranslations.exp_code == exp_code,
                ExperienceTranslations.lang_code == "az"
            )
        )
        az_translation = az_translation_query.scalar_one_or_none()
        if az_translation:
            az_translation.title = experience_request.title
            az_translation.university = experience_request.university

        en_translation_query = await db.execute(
            select(ExperienceTranslations).where(
                ExperienceTranslations.exp_code == exp_code,
                ExperienceTranslations.lang_code == "en"
            )
        )
        en_translation = en_translation_query.scalar_one_or_none()
        if en_translation:
            en_translation.title = translate_to_english(experience_request.title)
            en_translation.university = translate_to_english(experience_request.university)

        await db.commit()
        await db.refresh(experience)

        redis = await get_redis()
        keys = await redis.keys(f"experience:{experience.fin_kod}:*")
        for key in keys:
            await redis.delete(key)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "experience updated successfully.",
                "experience": {
                    "exp_code": experience.exp_code,
                    "start_date": experience.start_date,
                    "end_date": experience.end_date,
                    "updated_at": experience.updated_at.isoformat()
                }
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_experience(
    exp_code: str,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        result = await db.execute(select(Experience).where(Experience.exp_code == exp_code))
        experience = result.scalar_one_or_none()

        if not experience:
            return JSONResponse(
                content={"status_code": 404, "message": "experience not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        translations_query = await db.execute(
            select(ExperienceTranslations).where(ExperienceTranslations.exp_code == exp_code)
        )
        translations = translations_query.scalars().all()
        for translation in translations:
            await db.delete(translation)

        await db.delete(experience)
        await db.commit()

        # Clear Redis cache for this experience
        redis = await get_redis()
        keys = await redis.keys(f"experience:{experience.fin_kod}:*")
        for key in keys:
            await redis.delete(key)

        return JSONResponse(
            content={"status_code": 200, "message": "experience and translations deleted successfully."},
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )