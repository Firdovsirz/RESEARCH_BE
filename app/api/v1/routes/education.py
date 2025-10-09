from app.services.education import *
from app.api.v1.schemas.education import *
from app.db.session import get_db
from fastapi import Depends, status
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.utils.jwt_required import token_required
from fastapi import APIRouter

router = APIRouter()
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_education(
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required)
):
    return await add_education(education_request, db)

@router.get("/{fin_kod}", status_code=status.HTTP_200_OK)
async def get_education_endpoint(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required)
):
    return await get_education_by_code(fin_kod, lang_code, db)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_educations_endpoint(
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required)
):
    educations = await get_all_educations(db)
    education_list = [
        {
            "edu_code": edu.edu_code,
            "start_date": edu.start_date.isoformat(),
            "end_date": edu.end_date.isoformat() if edu.end_date else None,
            "created_at": edu.created_at.isoformat(),
            "updated_at": edu.updated_at.isoformat() if edu.updated_at else None
        }
        for edu in educations
    ]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"educations": education_list}
    )
@router.put("/{fin_kod}", status_code=status.HTTP_200_OK)
async def update_education_endpoint(
    edu_code: str,
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required)
):
    updated_education = await update_education(edu_code, education_request, db)
    if not updated_education:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Education not found"}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Education updated successfully",
            "education": {
                "edu_code": updated_education.edu_code,
                "start_date": updated_education.start_date.isoformat(),
                "end_date": updated_education.end_date.isoformat() if updated_education.end_date else None,
                "created_at": updated_education.created_at.isoformat(),
                "updated_at": updated_education.updated_at.isoformat() if updated_education.updated_at else None
            }
        }
    )
    