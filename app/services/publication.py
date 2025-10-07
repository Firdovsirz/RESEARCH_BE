import random
import asyncio
from datetime import datetime
from app.models.auth import Auth
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy import select, delete
from sqlalchemy.orm import subqueryload
from fastapi.responses import JSONResponse
from app.models.publication import Publication
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translations.publication_translation import PublicationTranslation
from app.api.v1.schemas.publication import (
    PublicationCreate,
    PublicationUpdate,
)
from app.models.publication_users import PublicationUsers 

def generate_publication_serial() -> str:
    number = random.randint(0, 99999)
    return f"PUBLICATION-{number:05d}"

# CREATE Publication
async def create_publication(
    publication_data: PublicationCreate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        existing_user_result = await db.execute(
            select(Auth).where(Auth.fin_kod == publication_data.fin_kod)
        )
        existing_user = existing_user_result.scalar_one_or_none()

        if not existing_user:
            return JSONResponse(
                content={
                    "status_code": 400,
                    "message": f"User with fin_kod '{publication_data.fin_kod}' does not exist!"
                }, status_code=status.HTTP_400_BAD_REQUEST
            )
        
        publication_code = generate_publication_serial()

        new_publication_user = PublicationUsers(
            publication_code=publication_code,
            name=publication_data.name,
            surname=publication_data.surname,
            email=publication_data.email
        )
        db.add(new_publication_user)
        await db.commit()

        new_publication = Publication(
            fin_kod=publication_data.fin_kod,
            publication_code=publication_code,
            publication_url=publication_data.publication_url,
            created_at=datetime.utcnow()
        )

        db.add(new_publication)
        await db.commit()
        await db.refresh(new_publication)

        # Create az translation
        az_translation = PublicationTranslation(
            publication_code=publication_code,
            lang_code="az",
            publication_name=publication_data.publication_name,
            created_at=datetime.utcnow()
        )
        db.add(az_translation)

        # Create en translation
        en_text = await asyncio.to_thread(translate_to_english, publication_data.publication_name, "az")
        en_translation = PublicationTranslation(
            publication_code=publication_code,
            lang_code="en",
            publication_name=en_text,
            created_at=datetime.utcnow()
        )
        db.add(en_translation)

        await db.commit()
        await db.refresh(new_publication)
        await db.refresh(az_translation)
        await db.refresh(en_translation)

        query = select(Publication).where(Publication.publication_code == new_publication.publication_code).options(subqueryload(Publication.translations))
        
        result = await db.execute(query)
        created_publication = result.scalar_one_or_none()

        translations = []
        if created_publication and created_publication.translations:
            for translation in created_publication.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "publication_name": translation.publication_name
                })

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Publication created successfully!",
                "data": {
                    "id": created_publication.id,
                    "fin_kod": created_publication.fin_kod,
                    "publication_code": created_publication.publication_code,
                    "publication_url": created_publication.publication_url,
                    "translations": translations,
                    "created_at": created_publication.created_at.isoformat() if created_publication.created_at else None
                }
            }, status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# GET All Publications
async def get_all_publications(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        result = await db.execute(
            select(Publication).options(subqueryload(Publication.translations))
        )
        publications = result.unique().scalars().all()

        publications_data = []
        for publication in publications:
            translations = []
            if publication.translations:
                for translation in publication.translations:
                    translations.append({
                        "lang_code": translation.lang_code,
                        "publication_name": translation.publication_name
                    })
                    
            user = await db.execute(
                select(PublicationUsers).where(PublicationUsers.publication_code == publication.publication_code)
            )
            user_info = user.scalar_one_or_none()
            

            publications_data.append({
                "id": publication.id,
                "fin_kod": publication.fin_kod,
                "name": user_info.name if user_info else None,
                "surname": user_info.surname if user_info else None,
                "email": user_info.email if user_info else None,
                "publication_code": publication.publication_code,
                "publication_url": publication.publication_url,
                "translations": translations,
                "created_at": publication.created_at.isoformat() if publication.created_at else None
            })
        
        if publications_data == []:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "Data not found!",
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        else:
            return JSONResponse(
                content={
                    "status_code": 200,
                    "message": "Publications retrieved successfully!",
                    "data": publications_data
                }, status_code=status.HTTP_200_OK
            )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# GET Publication by code with specific language
async def get_publication_by_code(
    fin_kod: str,
    lang: str,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        auth_result = await db.execute(
            select(Auth).where(Auth.fin_kod == fin_kod)
        )
        auth_user = auth_result.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Publication not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        publication_query = await db.execute(
            select(Publication)
            .where(Publication.fin_kod == fin_kod)
        )

        publications = publication_query.scalars().all()

        if not publications:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        publications_arr = []
        
        for publication in publications:


            translation_result = await db.execute(
                select(PublicationTranslation).where(
                    PublicationTranslation.publication_code == publication.publication_code,
                    PublicationTranslation.lang_code == lang
                )
            )

            translation = translation_result.scalar_one_or_none()

            if not translation:
                return JSONResponse(
                    content={
                        "status_code": 404,
                        "message": f"No translation found for language '{lang}'!"
                    }, status_code=status.HTTP_404_NOT_FOUND
                )
            
            publication_obj = {
                    "id": publication.id,
                    "fin_kod": publication.fin_kod,
                    "publication_url": publication.publication_url,
                    "publication_code": publication.publication_code,
                    "publication_name": translation.publication_name,
                    "lang_code": translation.lang_code,
                    "created_at": publication.created_at.isoformat() if publication.created_at else None
            }

            publications_arr.append(publication_obj)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Publication retrieved successfully!",
                "publications": publications_arr
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# UPDATE Publication
async def update_publication(
    publication_code: str,
    update_data: PublicationUpdate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        publication_result = await db.execute(
            select(Publication).where(Publication.publication_code == publication_code)
        )
        publication = publication_result.scalar_one_or_none()

        if not publication:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Publication not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Publication URL update
        if update_data.publication_url:
            publication.publication_url = update_data.publication_url

        # Update az translation
        az_translation_result = await db.execute(
            select(PublicationTranslation).where(
                PublicationTranslation.publication_code == publication_code,
                PublicationTranslation.lang_code == "az"
            )
        )
        az_translation = az_translation_result.scalar_one_or_none()
        
        if az_translation:
            az_translation.publication_name = update_data.publication_name
            az_translation.updated_at = datetime.utcnow()

        # Update en translation
        en_translation_result = await db.execute(
            select(PublicationTranslation).where(
                PublicationTranslation.publication_code == publication_code,
                PublicationTranslation.lang_code == "en"
            )
        )
        en_translation = en_translation_result.scalar_one_or_none()

        if en_translation:
            en_text = await asyncio.to_thread(translate_to_english, update_data.publication_name, "az")
            en_translation.publication_name = en_text
            en_translation.updated_at = datetime.utcnow()

        publication.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(publication)
        if az_translation:
            await db.refresh(az_translation)
        if en_translation:
            await db.refresh(en_translation)

        query = select(Publication).where(
            Publication.publication_code == publication_code
        ).options(subqueryload(Publication.translations))
        
        result = await db.execute(query)
        updated_publication = result.scalar_one_or_none()

        translations = []
        if updated_publication and updated_publication.translations:
            for translation in updated_publication.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "publication_name": translation.publication_name
                })

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Publication updated successfully",
                "data": {
                    "id": updated_publication.id,
                    "fin_kod": updated_publication.fin_kod,
                    "publication_code": updated_publication.publication_code,
                    "publication_url": updated_publication.publication_url,
                    "translations": translations,
                    "created_at": updated_publication.created_at.isoformat() if updated_publication.created_at else None,
                    "updated_at": updated_publication.updated_at.isoformat() if updated_publication.updated_at else None
                }
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# DELETE Publication
async def delete_publication(
    publication_code: str,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        publication_result = await db.execute(
            select(Publication).where(Publication.publication_code == publication_code)
        )
        publication = publication_result.scalar_one_or_none()

        if not publication:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Publication not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        await db.execute(delete(PublicationTranslation).where(PublicationTranslation.publication_code == publication_code))
        await db.execute(delete(Publication).where(Publication.publication_code == publication_code))
        await db.commit()

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Publication deleted successfully!"
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )