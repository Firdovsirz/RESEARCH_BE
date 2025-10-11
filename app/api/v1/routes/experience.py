from app.services.experience import *
from app.api.v1.schemas.experience import *
from app.db.session import get_db
from fastapi import Depends, status
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.utils.jwt_required import token_required
from fastapi import APIRouter

router = APIRouter()
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_experience(
    experience_request: CreateExperience,
    db: AsyncSession = Depends(get_db),
):
    return await add_experience(experience_request, db)

@router.get("/{fin_kod}", status_code=status.HTTP_200_OK)
async def get_experience_endpoint(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
):
    return await get_experience_by_code(fin_kod, lang_code, db)

@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_experiences_endpoint(
    db: AsyncSession = Depends(get_db),
):
    experiences = await get_all_experiences(db)
    experience_list = [
        {
            "exp_code": exp.exp_code,
            "start_date": exp.start_date.isoformat(),
            "end_date": exp.end_date.isoformat() if exp.end_date else None,
            "created_at": exp.created_at.isoformat(),
            "updated_at": exp.updated_at.isoformat() if exp.updated_at else None
        }
        for exp in experiences
    ]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"experiences": experience_list}
    )
@router.put("/{exp_code}", status_code=status.HTTP_200_OK)
async def update_experience_endpoint(
    exp_code: str,
    experience_request: CreateExperience,
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required)
):
    updated_experience = await update_experience(exp_code, experience_request, db)
    if not updated_experience:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "experience not found"}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "experience updated successfully",
            "experience": {
                "exp_code": updated_experience.exp_code,
                "start_date": updated_experience.start_date.isoformat(),
                "end_date": updated_experience.end_date.isoformat() if updated_experience.end_date else None,
                "created_at": updated_experience.created_at.isoformat(),
                "updated_at": updated_experience.updated_at.isoformat() if updated_experience.updated_at else None
            }
        }
    )
    