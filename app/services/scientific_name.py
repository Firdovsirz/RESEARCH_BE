import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status
from sqlalchemy import select, delete
from app.models.scientific_name import ScientificName
from sqlalchemy.orm import subqueryload
from fastapi.responses import JSONResponse
from app.models.auth import Auth
from app.models.scientific_name_translation import ScientificNameTranslation
from app.api.v1.schemas.scientific_name import (ScientificNameCreate, ScientificNameUpdate)
from app.utils.translator import translate_to_english
from app.db.session import get_db

# CREATE ScientificName
async def create_scientific_name(
    scientific_name_data: ScientificNameCreate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        existing_fin_kod_result = await db.execute(
            select(ScientificName).where(ScientificName.fin_kod == scientific_name_data.fin_kod)
        )
        existing_fin_kod_scientific_name = existing_fin_kod_result.scalar_one_or_none()

        if existing_fin_kod_scientific_name:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": f"User with fin_kod '{scientific_name_data.fin_kod}' already has an scientific_name!"
                },
                status_code=status.HTTP_409_CONFLICT
            )


        existing_scientific_name_result = await db.execute(
            select(ScientificName).where(ScientificName.scientific_name_code == scientific_name_data.scientific_name_code)
        )
        existing_scientific_name = existing_scientific_name_result.scalar_one_or_none()

        if existing_scientific_name:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": f"There is such an scientific_name_code!"
                },
                status_code=status.HTTP_409_CONFLICT
            )

        existing_user_result = await db.execute(
            select(Auth).where(Auth.fin_kod == scientific_name_data.fin_kod)
        )
        existing_user = existing_user_result.scalar_one_or_none()

        if not existing_user:
            return JSONResponse(
                content={
                    "status_code": 400,
                    "message": f"User with fin_kod '{scientific_name_data.fin_kod}' does not exist!"
                }, status_code=status.HTTP_400_BAD_REQUEST
            )


        new_scientific_name = ScientificName(
            fin_kod=scientific_name_data.fin_kod,
            scientific_name_code=scientific_name_data.scientific_name_code,
            created_at=datetime.utcnow()
        )

        db.add(new_scientific_name)
        await db.commit()
        await db.refresh(new_scientific_name)

        az_translation = ScientificNameTranslation(
            scientific_name_code=new_scientific_name.scientific_name_code,
            lang_code="az",
            scientific_name=scientific_name_data.scientific_name,
            created_at=datetime.utcnow()
        )
        db.add(az_translation)

        en_text = await asyncio.to_thread(translate_to_english, scientific_name_data.scientific_name, "az")
        en_translation = ScientificNameTranslation(
            scientific_name_code=new_scientific_name.scientific_name_code,
            lang_code="en",
            scientific_name=en_text,
            created_at=datetime.utcnow()
        )
        db.add(en_translation)

        await db.commit()
        await db.refresh(new_scientific_name)
        await db.refresh(az_translation)
        await db.refresh(en_translation)

        query = select(ScientificName).where(ScientificName.scientific_name_code == new_scientific_name.scientific_name_code).options(subqueryload(ScientificName.translations))
        
        result = await db.execute(query)
        created_scientific_name = result.scalar_one_or_none()

        translations = []
        if created_scientific_name and created_scientific_name.translations:
            for translation in created_scientific_name.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "scientific_name": translation.scientific_name
                })

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "ScientificName created successfully!",
                "data": {
                    "id": created_scientific_name.id,
                    "fin_kod": created_scientific_name.fin_kod,
                    "scientific_name_code": created_scientific_name.scientific_name_code,
                    "translations": translations,
                    "created_at": created_scientific_name.created_at.isoformat() if created_scientific_name.created_at else None
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

# GET All ScientificNames
async def get_all_scientific_names(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        result = await db.execute(
            select(ScientificName).options(subqueryload(ScientificName.translations))
        )
        scientific_names = result.unique().scalars().all()

        scientific_names_data = []
        for scientific_name in scientific_names:
            translations = []
            if scientific_name.translations:
                for translation in scientific_name.translations:
                    translations.append({
                        "lang_code": translation.lang_code,
                        "scientific_name": translation.scientific_name
                    })

            scientific_names_data.append({
                "id": scientific_name.id,
                "fin_kod": scientific_name.fin_kod,
                "scientific_name_code": scientific_name.scientific_name_code,
                "translations": translations,
                "created_at": scientific_name.created_at.isoformat() if scientific_name.created_at else None
            })
        
        if scientific_names_data == []:
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
                    "message": "ScientificNames retrieved successfully!",
                    "data": scientific_names_data
                }, status_code=status.HTTP_200_OK
            )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# GET ScientificName by code with specific language
async def get_scientific_name_by_code(
    scientific_name_code: str,
    lang: str,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        scientific_name_result = await db.execute(
            select(ScientificName).where(ScientificName.scientific_name_code == scientific_name_code)
        )
        scientific_name = scientific_name_result.scalar_one_or_none()

        if not scientific_name:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Scientific name not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        translation_result = await db.execute(
            select(ScientificNameTranslation).where(
                ScientificNameTranslation.scientific_name_code == scientific_name_code,
                ScientificNameTranslation.lang_code == lang
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
                "message": "ScientificName retrieved successfully!",
                "data": {
                    "id": scientific_name.id,
                    "fin_kod": scientific_name.fin_kod,
                    "scientific_name_code": scientific_name.scientific_name_code,
                    "scientific_name": translation.scientific_name,
                    "lang_code": translation.lang_code,
                    "created_at": scientific_name.created_at.isoformat() if scientific_name.created_at else None
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

# UPDATE ScientificName
async def update_scientific_name(
    scientific_name_code: str,
    update_data: ScientificNameUpdate,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        scientific_name_result = await db.execute(
            select(ScientificName).where(ScientificName.scientific_name_code == scientific_name_code)
        )
        scientific_name = scientific_name_result.scalar_one_or_none()

        if not scientific_name:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Scientific name not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        az_translation_result = await db.execute(
            select(ScientificNameTranslation).where(
                ScientificNameTranslation.scientific_name_code == scientific_name_code,
                ScientificNameTranslation.lang_code == "az"
            )
        )
        az_translation = az_translation_result.scalar_one_or_none()
        
        if az_translation:
            az_translation.scientific_name = update_data.scientific_name
            az_translation.updated_at = datetime.utcnow()

        en_translation_result = await db.execute(
            select(ScientificNameTranslation).where(
                ScientificNameTranslation.scientific_name_code == scientific_name_code,
                ScientificNameTranslation.lang_code == "en"
            )
        )
        en_translation = en_translation_result.scalar_one_or_none()

        if en_translation:
            en_text = await asyncio.to_thread(translate_to_english, update_data.scientific_name, "az")
            en_translation.scientific_name = en_text
            en_translation.updated_at = datetime.utcnow()

        scientific_name.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(scientific_name)
        if az_translation:
            await db.refresh(az_translation)
        if en_translation:
            await db.refresh(en_translation)

        query = select(ScientificName).where(
            ScientificName.scientific_name_code == scientific_name_code
        ).options(subqueryload(ScientificName.translations))
        
        result = await db.execute(query)
        updated_scientific_name = result.scalar_one_or_none()

        translations = []
        if updated_scientific_name and updated_scientific_name.translations:
            for translation in updated_scientific_name.translations:
                translations.append({
                    "lang_code": translation.lang_code,
                    "scientific_name": translation.scientific_name
                })

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Scientific name updated successfully!",
                "data": {
                    "id": updated_scientific_name.id,
                    "fin_kod": updated_scientific_name.fin_kod,
                    "scientific_name_code": updated_scientific_name.scientific_name_code,
                    "translations": translations,
                    "created_at": updated_scientific_name.created_at.isoformat() if updated_scientific_name.created_at else None,
                    "updated_at": updated_scientific_name.updated_at.isoformat() if updated_scientific_name.updated_at else None
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

# DELETE ScientificName
async def delete_scientific_name(
    scientific_name_code: str,
    db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        scientific_name_result = await db.execute(
            select(ScientificName).where(ScientificName.scientific_name_code == scientific_name_code)
        )
        scientific_name = scientific_name_result.scalar_one_or_none()

        if not scientific_name:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Scientific name not found!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        await db.execute(delete(ScientificNameTranslation).where(ScientificNameTranslation.scientific_name_code == scientific_name_code))
        await db.execute(delete(ScientificName).where(ScientificName.scientific_name_code == scientific_name_code))
        await db.commit()

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Scientific name deleted successfully!"
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