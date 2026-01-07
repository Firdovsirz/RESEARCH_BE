from fastapi import APIRouter
from app.services.links import *
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.api.v1.schemas.links import *
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required
from app.utils.api_key_checker import check_api_key

router = APIRouter()
@router.post(
    "/create",
    response_model=LinksOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add Links",
    tags=["Links"],
)
async def add_links_endpoint(
    links: LinksCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
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
    "/{fin_kod}",
    response_model=LinksOut,
    status_code=status.HTTP_200_OK,
    summary="Get Links by FIN code",
    tags=["Links"],
)
async def get_links_endpoint(
    fin_kod: str,
    api_key: str = Depends(check_api_key),
    db: AsyncSession = Depends(get_db),
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
    "/{fin_kod}/update",
    response_model=LinksOut,
    status_code=status.HTTP_200_OK,
    summary="Update Links by FIN code",
    tags=["Links"],
)
async def update_links_endpoint(
    fin_kod: str,
    links_update: LinksUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    response = await update_links_service(
        links_update,
        fin_kod=fin_kod,
        db=db,
    )
    if isinstance(response, JSONResponse):
        return response
    return LinksOut.from_orm(response)

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

@router.delete(
    "/{link_id}/delete/{url_name}",
    status_code=status.HTTP_200_OK,
    summary="Delete Links by FIN code",
    tags=["Links"],
)
async def delete_links_endpoint(
    link_id: int,
    url_name: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(token_required([0, 1, 2]))
):
    response = await delete_links_service(
        link_id=link_id,
        url_name=url_name,
        db=db,
    )
    return response