import random
from datetime import datetime
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.education import Education
from app.models.education_translation import EducationTranslation
from app.api.v1.schemas.education import CreateEducation


def generate_edu_code():
    """Generate a unique 7-character alphanumeric code."""
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7))


async def add_education(
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        edu_code = generate_edu_code()

        new_education = Education(
            edu_code=edu_code,
            start_date=education_request.start_date,  # integer year
            end_date=education_request.end_date,      # integer year or None
            created_at=datetime.utcnow()
        )

        new_translation = EducationTranslation(
            edu_code=edu_code,
            lang_code="en",             # default example
            tittle=education_request.tittle if hasattr(education_request, 'tittle') else "Sample Title",
            university=education_request.university if hasattr(education_request, 'university') else "Sample University"
        )

        db.add(new_education)
        db.add(new_translation)
        await db.commit()
        await db.refresh(new_education)
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


async def get_education_by_code(
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

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Education fetched successfully.",
                "education": {
                    "edu_code": education.edu_code,
                    "start_date": education.start_date,
                    "end_date": education.end_date,
                    "created_at": education.created_at.isoformat(),
                    "updated_at": education.updated_at.isoformat() if education.updated_at else None
                }
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
