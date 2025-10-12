import random
from datetime import datetime
from app.db.database import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.education import Education
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.api.v1.schemas.education import CreateEducation
from app.models.education_translation import EducationTranslation


def generate_edu_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7))


async def add_education(
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        edu_code = generate_edu_code()

        new_education = Education(
            edu_code=edu_code,
            fin_kod=education_request.fin_kod,
            start_date=education_request.start_date,
            end_date=education_request.end_date,
            created_at=datetime.utcnow()
        )

        new_translation_az = EducationTranslation(
            edu_code=edu_code,
            lang_code="az",
            title=education_request.title,
            university=education_request.university
        )

        new_translation = EducationTranslation(
            edu_code=edu_code,
            lang_code="en",
            title=translate_to_english(education_request.title),
            university=translate_to_english(education_request.university)
        )

        db.add(new_education)
        db.add(new_translation_az)
        db.add(new_translation)
        await db.commit()
        await db.refresh(new_education)
        await db.refresh(new_translation_az)
        await db.refresh(new_translation)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Education added successfully.",
                "edu_code": edu_code
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

from app.db.redis_client import get_redis
import json

async def get_education_by_code(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        redis = await get_redis()
        cache_key = f"education:{fin_kod}:{lang_code}"

        cached_data = await redis.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return JSONResponse(
                content={
                    "status_code": 200,
                    "message": "Education fetched successfully (from cache).",
                    "educations": json.loads(cached_data)
                },
                status_code=status.HTTP_200_OK
            )

        print("CACHE MISS")

        result = await db.execute(
            select(Education)
            .where(Education.fin_kod == fin_kod)
            .order_by(Education.start_date.desc())
        )

        educations = result.scalars().all()
        if not educations:
            return JSONResponse(
                content={"status_code": 204, "message": "NO CONTENT"},
                status_code=status.HTTP_204_NO_CONTENT
            )

        education_arr = []
        for education in educations:
            edu_translation_query = await db.execute(
                select(EducationTranslation)
                .where(
                    EducationTranslation.edu_code == education.edu_code,
                    EducationTranslation.lang_code == lang_code
                )
            )
            edu_translation = edu_translation_query.scalar_one_or_none()

            edu_obj = {
                "fin_kod": education.fin_kod,
                "start_date": education.start_date,
                "end_date": education.end_date,
                "title": edu_translation.title,
                "university": edu_translation.university
            }
            education_arr.append(edu_obj)

        await redis.set(cache_key, json.dumps(education_arr), ex=3600)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Education fetched successfully.",
                "educations": education_arr
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_all_educations(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        result = await db.execute(select(Education))
        educations = result.scalars().all()

        if not educations:
            return JSONResponse(
                content={"status_code": 204, "message": "No educations found"},
                status_code=status.HTTP_204_NO_CONTENT
            )

        educations_list = [
            {
                "edu_code": edu.edu_code,
                "start_date": edu.start_date,
                "end_date": edu.end_date,
                "created_at": edu.created_at.isoformat(),
                "updated_at": edu.updated_at.isoformat() if edu.updated_at else None
            }
            for edu in educations
        ]

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Educations fetched successfully.",
                "educations": educations_list
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_education(
    edu_code: str,
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        result = await db.execute(select(Education).where(Education.edu_code == edu_code))
        education = result.scalar_one_or_none()

        if not education:
            return JSONResponse(
                content={"status_code": 404, "message": "Education not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        education.start_date = education_request.start_date
        education.end_date = education_request.end_date
        education.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(education)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Education updated successfully.",
                "education": {
                    "edu_code": education.edu_code,
                    "start_date": education.start_date,
                    "end_date": education.end_date,
                    "updated_at": education.updated_at.isoformat()
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

async def delete_education(
    edu_code: str,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        result = await db.execute(select(Education).where(Education.edu_code == edu_code))
        education = result.scalar_one_or_none()

        if not education:
            return JSONResponse(
                content={"status_code": 404, "message": "Education not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        await db.delete(education)
        await db.commit()

        return JSONResponse(
            content={"status_code": 200, "message": "Education deleted successfully."},
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"status_code": 500, "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
