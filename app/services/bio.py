import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status
from sqlalchemy import select, delete
from app.models.bio import Bio
from sqlalchemy.orm import subqueryload
from fastapi.responses import JSONResponse
from app.models.auth import Auth
from app.models.translations.bio_translation import BioTranslation
from app.api.v1.schemas.bio import (BioCreate, BioUpdate)
from app.utils.translator import translate_to_english
from app.db.session import get_db

# CREATE Bio
async def create_bio(
    bio_data: BioCreate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        existing_fin_kod_result = await db.execute(
            select(Bio).where(Bio.fin_kod == bio_data.fin_kod)
        )
        existing_fin_kod_bio = existing_fin_kod_result.scalar_one_or_none()

        if existing_fin_kod_bio:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": f"User with fin_kod '{bio_data.fin_kod}' already has an bio!"
                },
                status_code=status.HTTP_409_CONFLICT
            )


        existing_bio_result = await db.execute(
            select(Bio).where(Bio.bio_code == bio_data.bio_code)
        )
        existing_bio = existing_bio_result.scalar_one_or_none()

        if existing_bio:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": f"There is such an bio!"
                },
                status_code=status.HTTP_409_CONFLICT
            )

        existing_user_result = await db.execute(
            select(Auth).where(Auth.fin_kod == bio_data.fin_kod)
        )
        existing_user = existing_user_result.scalar_one_or_none()

        if not existing_user:
            return JSONResponse(
                content={
                    "status_code": 400,
                    "message": f"User with fin_kod '{bio_data.fin_kod}' does not exist!"
                }, status_code=status.HTTP_400_BAD_REQUEST
            )


        new_bio = Bio(
            fin_kod=bio_data.fin_kod,
            bio_code=bio_data.bio_code,
            created_at=datetime.utcnow()
        )

        db.add(new_bio)
        await db.commit()
        await db.refresh(new_bio)

        az_translation = BioTranslation(
            bio_code=new_bio.bio_code,
            lang_code="az",
            bio_field=bio_data.bio_field,
            created_at=datetime.utcnow()
        )
        db.add(az_translation)

        en_text = await asyncio.to_thread(translate_to_english, bio_data.bio_field, "az")
        en_translation = BioTranslation(
            bio_code=new_bio.bio_code,
            lang_code="en",
            bio_field=en_text,
            created_at=datetime.utcnow()
        )
        db.add(en_translation)

        await db.commit()
        await db.refresh(new_bio)
        await db.refresh(az_translation)
        await db.refresh(en_translation)

        query = select(Bio).where(Bio.bio_code == new_bio.bio_code).options(subqueryload(Bio.translations))
        
        result = await db.execute(query)
        created_bio = result.scalar_one_or_none()

        translations = []
        if created_bio and created_bio.translations:
            for translation in created_bio.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "bio_field": translation.bio_field
                })

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Bio created successfully!",
                "data": {
                    "id": created_bio.id,
                    "fin_kod": created_bio.fin_kod,
                    "bio_code": created_bio.bio_code,
                    "translations": translations,
                    "created_at": created_bio.created_at.isoformat() if created_bio.created_at else None
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

# GET All Bios
async def get_all_bios(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        result = await db.execute(
            select(Bio).options(subqueryload(Bio.translations))
        )
        bios = result.unique().scalars().all()

        bios_data = []
        for bio in bios:
            translations = []
            if bio.translations:
                for translation in bio.translations:
                    translations.append({
                        "lang_code": translation.lang_code,
                        "bio_field": translation.bio_field
                    })

            bios_data.append({
                "id": bio.id,
                "fin_kod": bio.fin_kod,
                "bio_code": bio.bio_code,
                "translations": translations,
                "created_at": bio.created_at.isoformat() if bio.created_at else None
            })
        
        if bios_data == []:
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
                    "message": "Bios retrieved successfully!",
                    "data": bios_data
                }, status_code=status.HTTP_200_OK
            )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# GET Bio by code with specific language
async def get_bio_by_code(
    bio_code: str,
    lang: str,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        bio_result = await db.execute(
            select(Bio).where(Bio.bio_code == bio_code)
        )
        bio = bio_result.scalar_one_or_none()

        if not bio:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Bio not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        translation_result = await db.execute(
            select(BioTranslation).where(
                BioTranslation.bio_code == bio_code,
                BioTranslation.lang_code == lang
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

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Bio retrieved successfully!",
                "data": {
                    "id": bio.id,
                    "fin_kod": bio.fin_kod,
                    "bio_code": bio.bio_code,
                    "bio_field": translation.bio_field,
                    "lang_code": translation.lang_code,
                    "created_at": bio.created_at.isoformat() if bio.created_at else None
                }
            }, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# UPDATE Bio
async def update_bio(
    bio_code: str,
    update_data: BioUpdate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        bio_result = await db.execute(
            select(Bio).where(Bio.bio_code == bio_code)
        )
        bio = bio_result.scalar_one_or_none()

        if not bio:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Bio not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        az_translation_result = await db.execute(
            select(BioTranslation).where(
                BioTranslation.bio_code == bio_code,
                BioTranslation.lang_code == "az"
            )
        )
        az_translation = az_translation_result.scalar_one_or_none()
        
        if az_translation:
            az_translation.bio_field = update_data.bio_field
            az_translation.updated_at = datetime.utcnow()

        en_translation_result = await db.execute(
            select(BioTranslation).where(
                BioTranslation.bio_code == bio_code,
                BioTranslation.lang_code == "en"
            )
        )
        en_translation = en_translation_result.scalar_one_or_none()

        if en_translation:
            en_text = await asyncio.to_thread(translate_to_english, update_data.bio_field, "az")
            en_translation.bio_field = en_text
            en_translation.updated_at = datetime.utcnow()

        bio.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(bio)
        if az_translation:
            await db.refresh(az_translation)
        if en_translation:
            await db.refresh(en_translation)

        query = select(Bio).where(
            Bio.bio_code == bio_code
        ).options(subqueryload(Bio.translations))
        
        result = await db.execute(query)
        updated_bio = result.scalar_one_or_none()

        translations = []
        if updated_bio and updated_bio.translations:
            for translation in updated_bio.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "bio_field": translation.bio_field
                })

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Bio updated successfully",
                "data": {
                    "id": updated_bio.id,
                    "fin_kod": updated_bio.fin_kod,
                    "bio_code": updated_bio.bio_code,
                    "translations": translations,
                    "created_at": updated_bio.created_at.isoformat() if updated_bio.created_at else None,
                    "updated_at": updated_bio.updated_at.isoformat() if updated_bio.updated_at else None
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

# DELETE Bio
async def delete_bio(
    bio_code: str,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        bio_result = await db.execute(
            select(Bio).where(Bio.bio_code == bio_code)
        )
        bio = bio_result.scalar_one_or_none()

        if not bio:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Bio not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        await db.execute(delete(BioTranslation).where(BioTranslation.bio_code == bio_code))
        await db.execute(delete(Bio).where(Bio.bio_code == bio_code))
        await db.commit()

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Bio deleted successfully!"
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