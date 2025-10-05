from app.services.links import *
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.api.v1.schemas.links import *
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from fastapi import APIRouter

router = APIRouter()
@router.post(
    "/links-create/",
    response_model=LinksOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add Links",
    tags=["Links"],
)
async def add_links_endpoint(
    links: LinksCreate,
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required),
):
    response = await add_links_service(
        links,
        db=db,
    )
    if isinstance(response, JSONResponse):
        return response
    return LinksOut.from_orm(response)

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

@router.get(
    "/links/profile/{fin_kod}",
    response_model=LinksOut,
    status_code=status.HTTP_200_OK,
    summary="Get Links by FIN code",
    tags=["Links"],
)
async def get_links_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required),
):
    response = await get_links_service(
        fin_kod=fin_kod,
        db=db,
    )
    if isinstance(response, JSONResponse):
        return response
    return LinksOut.from_orm(response)

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

@router.put(
    "/links/update/{fin_kod}",
    response_model=LinksOut,
    status_code=status.HTTP_200_OK,
    summary="Update Links by FIN code",
    tags=["Links"],
)
async def update_links_endpoint(
    fin_kod: str,
    links_update: LinksUpdate,
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required),
):
    response = await update_links_service(
        fin_kod=fin_kod,
        scopus_url=links_update.scopus_url,
        google_scholar_url=links_update.google_scholar_url,
        webofscience_url=links_update.webofscience_url,
        db=db,
    )
    if isinstance(response, JSONResponse):
        return response
    return LinksOut.from_orm(response)

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

@router.delete(
    "/links/delete/{fin_kod}",
    status_code=status.HTTP_200_OK,
    summary="Delete Links by FIN code",
    tags=["Links"],
)
async def delete_links_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(token_required),
):
    response = await delete_links_service(
        fin_kod=fin_kod,
        db=db,
    )
    return response