from fastapi import APIRouter
from app.db.session import get_db
from fastapi import Depends, status
from app.services.education import *
from app.api.v1.schemas.education import *
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.utils.api_key_checker import check_api_key

router = APIRouter()
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_education(
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await add_education(education_request, db)

@router.get("/{fin_kod}", status_code=status.HTTP_200_OK)
async def get_education_endpoint(
    fin_kod: str,
    api_key: str = Depends(check_api_key),
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_education_by_code(fin_kod, lang_code, db)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_educations_endpoint(
    api_key: str = Depends(check_api_key),
    db: AsyncSession = Depends(get_db)
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
@router.put("/{edu_code}/update")
async def update_education_endpoint(
    edu_code: str,
    education_request: CreateEducation,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await update_education(edu_code, education_request, db)

@router.delete("/{edu_code}/delete")
async def delete_education_endpoint(
    edu_code: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    return await delete_education(edu_code, db)