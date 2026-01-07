from app.utils.otp import *
from app.utils.email import *
from app.models.user import User
from app.utils.password import *
from app.db.session import get_db
from fastapi import Depends, status
from app.models.links import Links 
from sqlalchemy.future import select
from app.api.v1.schemas.links import *
from app.db.redis_client import get_redis
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def add_links_service(request: LinksCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if user exists
        query = select(User).where(User.fin_kod == request.fin_kod)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status_code": 404, "message": "User not found"},
            )

        # Check if Links row exists
        query = select(Links).where(Links.fin_kod == request.fin_kod)
        result = await db.execute(query)
        links_entry = result.scalars().first()

        if links_entry:
            # Check if the column is already filled for each provided URL
            if request.scopus_url and links_entry.scopus_url:
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"status_code": 409, "message": "Scopus URL already exists"}
                )
            if request.google_scholar_url and links_entry.google_scholar_url:
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"status_code": 409, "message": "Google Scholar URL already exists"}
                )
            if request.webofscience_url and links_entry.webofscience_url:
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"status_code": 409, "message": "Web of Science URL already exists"}
                )
            if request.linkedin_url and links_entry.linkedin_url:
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"status_code": 409, "message": "LinkedIn URL already exists"}
                )

            # Update only the fields that are provided
            if request.scopus_url is not None:
                links_entry.scopus_url = request.scopus_url
            if request.google_scholar_url is not None:
                links_entry.google_scholar_url = request.google_scholar_url
            if request.webofscience_url is not None:
                links_entry.webofscience_url = request.webofscience_url
            if request.linkedin_url is not None:
                links_entry.linkedin_url = request.linkedin_url

            db.add(links_entry)
            await db.commit()
            await db.refresh(links_entry)

            # Clear cache
            redis = await get_redis()
            await redis.delete(f"links:{request.fin_kod}")

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 201, "message": "Links entry updated successfully"},
            )

        # If no row exists, create a new one
        new_links = Links(
            fin_kod=request.fin_kod,
            scopus_url=request.scopus_url,
            google_scholar_url=request.google_scholar_url,
            webofscience_url=request.webofscience_url,
            linkedin_url=request.linkedin_url
        )
        db.add(new_links)
        await db.commit()
        await db.refresh(new_links)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"status_code": 201, "message": "Links entry added successfully"},
        )

    except HTTPException as http_exc:
        if http_exc.status_code == 422:
            logger.error(f"Validation error while adding links: {http_exc.detail}")
        else:
            logger.error(f"HTTP error while adding links: {http_exc.detail}")
        await db.rollback()
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"status_code": http_exc.status_code, "message": str(http_exc.detail)}
        )

    except Exception as e:
        await db.rollback()
        logger.exception(f"Unexpected error while adding links: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status_code": 500, "message": f"An error occurred: {str(e)}"},
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
                    "id": scopus_entry.id,
                    "fin_kod": scopus_entry.fin_kod,
                    "scopus_url": scopus_entry.scopus_url,
                    "web_of_science": scopus_entry.webofscience_url,
                    "google_scholar": scopus_entry.google_scholar_url,
                    "linkedin_url": scopus_entry.linkedin_url
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
        scopus_entry.webofscience_url = request.webofscience_url
        scopus_entry.google_scholar_url = request.google_scholar_url
        scopus_entry.linkedin_url = request.linkedin_url
        db.add(scopus_entry)
        await db.commit()
        await db.refresh(scopus_entry)
        redis = await get_redis()
        await redis.delete(f"links:{fin_kod}")
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
    link_id: int,
    url_name: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Links).where(Links.id == link_id)
        result = await db.execute(query)
        scopus_entry = result.scalars().first()
        if not scopus_entry:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status_code": 404,
                    "message": "Links entry not found"
                },
            )

        if not hasattr(Links, url_name):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status_code": 400,
                    "message": f"Column '{url_name}' does not exist in Links"
                },
            )

        setattr(scopus_entry, url_name, None)
        db.add(scopus_entry)
        await db.commit()
        await db.refresh(scopus_entry)
        
        # Clear cache by fin_kod
        redis = await get_redis()
        await redis.delete(f"links:{scopus_entry.fin_kod}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": f"'{url_name}' deleted successfully"
            },
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"An error occurred: {str(e)}"},
        )