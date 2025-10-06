from app.utils.otp import *
from app.utils.email import *
from app.models.user import User
from app.utils.password import *
from app.db.session import get_db
from fastapi import Depends, status
from app.models.links import Links 
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.links import *

async def add_links_service(request: LinksCreate, db: AsyncSession = Depends(get_db)):
    try:
        query = select(User).where(User.fin_kod == request.fin_kod)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "User not found"},
            )
        query = select(Links).where(Links.fin_kod == request.fin_kod)
        result = await db.execute(query)
        scopus_entry = result.scalars().first()
        if scopus_entry:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Links entry already exists for this user"},
            )
        new_links = Links(fin_kod=request.fin_kod, scopus_url=request.scopus_url, google_scholar_url=request.google_scholar_url, webofscience_url=request.webofscience_url)
        db.add(new_links)
        await db.commit()
        await db.refresh(new_links)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Links entry added successfully"},
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"An error occurred: {str(e)}"},
        )
    
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def get_links_service(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Links).where(Links.fin_kod == fin_kod)
        result = await db.execute(query)
        scopus_entry = result.scalars().first()
        if not scopus_entry:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Scopus entry not found for this user"},
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "data": {
                    "fin_kod": scopus_entry.fin_kod,
                    "scopus_url": scopus_entry.scopus_url,
                    "web_of_science": scopus_entry.webofscience_url,
                    "google_scholar": scopus_entry.google_scholar_url
                }
            }
        )
    except Exception as e:
        logger.exception(f"Error fetching Links entry for fin_kod={fin_kod}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"An error occurred: {str(e)}"},
        )

async def update_links_service(
    request: LinksUpdate,
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Links).where(Links.fin_kod == fin_kod)
        result = await db.execute(query)
        scopus_entry = result.scalars().first()
        if not scopus_entry:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status_code": 404,
                    "message": "Scopus entry not found for this user"
                }
            )
        scopus_entry.scopus_url = request.scopus_url
        db.add(scopus_entry)
        await db.commit()
        await db.refresh(scopus_entry)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": "Scopus entry updated successfully"
            }
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": f"An error occurred: {str(e)}"
            }
        )
    
async def delete_links_service(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Links).where(Links.fin_kod == fin_kod)
        result = await db.execute(query)
        scopus_entry = result.scalars().first()
        if not scopus_entry:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Scopus entry not found for this user"},
            )
        await db.delete(scopus_entry)
        await db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Scopus entry deleted successfully"},
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"An error occurred: {str(e)}"},
        )