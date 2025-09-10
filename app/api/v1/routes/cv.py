from app.services.cv import *
from app.db.session import get_db
from app.api.v1.schemas.cv import *
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required

router = APIRouter()

# Get cv endpoint ("/api/cv/{fin_kod}")
# Get cv by user's fin kod
# Return cv if the cv is available in /static/cv/{fin_kod}/CV_{fin_kod}_{current_year} path

@router.get("/{fin_kod}")
async def get_cv_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    return await get_cv(fin_kod, db)

# Add cv endpoint ("/api/cv/create")
# Add cv for user upload cv as a file
# Cv will be saved in /stativc/cv/ path with /{fin_kod} folder and the name /{fin_kod}/CV_{fin_kod}_{current_year}

@router.post("/create")
async def add_cv_endpoint(
    cv_request: CreateCv = Depends(CreateCv.as_form),
    db: AsyncSession = Depends(get_db)
):
    return await add_cv(cv_request, db)