from app.services.scopus import *
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.api.v1.schemas.scopus import *
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from fastapi import APIRouter

router = APIRouter()
@router.post(
    "/scopus-create",
    response_model=ScopusOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add Scopus URL",
    tags=["Scopus"],
)
async def add_scopus_endpoint(
    scopus: ScopusCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(token_required),
):
    response = await add_scopus_service(
        fin_kod=scopus.fin_kod,
        scopus_url=scopus.scopus_url,
        db=db,
    )
    if isinstance(response, JSONResponse):
        return response
    return ScopusOut.from_orm(response)

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

@router.get(
    "/get-scopus-profile/{fin_kod}",
    response_model=ScopusOut,
    status_code=status.HTTP_200_OK,
    summary="Get Scopus URL by FIN code",
    tags=["Scopus"],
)
async def get_scopus_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(token_required),
):
    response = await get_scopus_service(
        fin_kod=fin_kod,
        db=db,
    )
    if isinstance(response, JSONResponse):
        return response
    return ScopusOut.from_orm(response)

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

@router.put(
    "/scopus/{fin_kod}/update",
    response_model=ScopusOut,
    status_code=status.HTTP_200_OK,
    summary="Update Scopus URL by FIN code",
    tags=["Scopus"],
)
async def update_scopus_endpoint(
    fin_kod: str,
    scopus_update: ScopusUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(token_required),
):
    response = await update_scopus_service(
        fin_kod=fin_kod,
        scopus_url=scopus_update.scopus_url,
        db=db,
    )
    if isinstance(response, JSONResponse):
        return response
    return ScopusOut.from_orm(response)

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

@router.delete(
    "/scopus/{fin_kod}/delete",
    status_code=status.HTTP_200_OK,
    summary="Delete Scopus URL by FIN code",
    tags=["Scopus"],
)
async def delete_scopus_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(token_required),
):
    response = await delete_scopus_service(
        fin_kod=fin_kod,
        db=db,
    )
    return response