from app.utils.otp import *
from app.utils.email import *
from app.models.user import User
from app.utils.password import *
from app.db.session import get_db
from fastapi import Depends, status
from app.models.scopus import Scopus
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

async def add_scopus_service(
    fin_kod: str,
    scopus_url: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(User).where(User.fin_kod == fin_kod)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "User not found"},
            )
        query = select(Scopus).where(Scopus.fin_kod == fin_kod)
        result = await db.execute(query)
        scopus_entry = result.scalars().first()
        if scopus_entry:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Scopus entry already exists for this user"},
            )
        new_scopus = Scopus(fin_kod=fin_kod, scopus_url=scopus_url)
        db.add(new_scopus)
        await db.commit()
        await db.refresh(new_scopus)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Scopus entry added successfully"},
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

async def get_scopus_service(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Scopus).where(Scopus.fin_kod == fin_kod)
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
                "fin_kod": scopus_entry.fin_kod,
                "scopus_url": scopus_entry.scopus_url
            },
        )
    except Exception as e:
        logger.exception(f"Error fetching Scopus entry for fin_kod={fin_kod}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"An error occurred: {str(e)}"},
        )

async def update_scopus_service(
    fin_kod: str,
    scopus_url: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Scopus).where(Scopus.fin_kod == fin_kod)
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
        scopus_entry.scopus_url = scopus_url
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
    
async def delete_scopus_service(
    fin_kod: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Scopus).where(Scopus.fin_kod == fin_kod)
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