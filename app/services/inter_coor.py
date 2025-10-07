import random
from datetime import datetime
from sqlalchemy import select
from app.models.auth import Auth
from app.db.session import get_db
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.inter_coor import InterCoor
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.api.v1.schemas.inter_coor import CreateInterCoor
from app.models.translations.inter_coor_translations import InterCoorTranslations
import logging
from app.models.inter_corp_users import InternationalCorporationsUsers

logger = logging.getLogger(__name__)

def generate_inter_coor_serial() -> str:
    number = random.randint(0, 99999)
    return f"INTER_CORP-{number:05d}"

async def create_inter_coor (
    inter_coor_request: CreateInterCoor,
    db: AsyncSession = Depends(get_db)
):
    try:
        existing_user_result = await db.execute(
            select(Auth).where(Auth.fin_kod == inter_coor_request.fin_kod)
        )
        existing_user = existing_user_result.scalar_one_or_none()

        if not existing_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": f"User with fin_kod '{inter_coor_request.fin_kod}' does not exist!"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        inter_coor_code = generate_inter_coor_serial()
        
        new_inter_coor = InterCoor(
            fin_kod=inter_coor_request.fin_kod,
            inter_corp_code=inter_coor_code,
            created_at=datetime.utcnow()
        )
        new_inter_coor_user = InternationalCorporationsUsers(
            name = inter_coor_request.name,
            surname = inter_coor_request.surname,
            email = inter_coor_request.email,
            image = inter_coor_request.image,
            inter_corp_code = inter_coor_code
        )


        new_inter_coor_az = InterCoorTranslations(
            inter_corp_code=inter_coor_code,
            language_code="az",             
            inter_corp_name=inter_coor_request.inter_coor_name,
            created_at=datetime.utcnow()
        )

        new_inter_coor_en = InterCoorTranslations(
            inter_corp_code=inter_coor_code,
            language_code="en",
            inter_corp_name=translate_to_english(inter_coor_request.inter_coor_name),
            created_at=datetime.utcnow()            
        )
        db.add(new_inter_coor_user)
        db.add(new_inter_coor)
        db.add(new_inter_coor_az)
        db.add(new_inter_coor_en)

        await db.commit()

        await db.refresh(new_inter_coor)
        await db.refresh(new_inter_coor_az)
        await db.refresh(new_inter_coor_en)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "Inter coor created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        await db.rollback()
        logger.error("Error in create_inter_coor", exc_info=True)
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_inter_corp_by_fin (
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == fin_kod)
        )

        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        inter_corp_arr = []

        inter_corps_query = await db.execute(
            select(InterCoor)
            .where(InterCoor.fin_kod == fin_kod)
        )

        inter_corps = inter_corps_query.scalars().all()

        if not inter_corps:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        for inter_corp in inter_corps:
            inter_corp_translation_query = await db.execute(
                select(InterCoorTranslations)
                .where(
                    InterCoorTranslations.inter_corp_code == inter_corp.inter_corp_code,
                    InterCoorTranslations.language_code == lang_code
                )
            )

            user_query_inter_corp = await db.execute(
                select(InternationalCorporationsUsers)
                .where(InternationalCorporationsUsers.inter_corp_code == inter_corp.inter_corp_code)
            )

            user_corp = user_query_inter_corp.scalar_one_or_none()

            inter_corp_translation = inter_corp_translation_query.scalar_one_or_none()

            inter_corp_obj = {
                "inter_corp_name": inter_corp_translation.inter_corp_name,
                "inter_corp_code": inter_corp_translation.inter_corp_code,
                "name": user_corp.name if user_corp else None,
                "surname": user_corp.surname if user_corp else None,
                "email": user_corp.email if user_corp else None
            }

            inter_corp_arr.append(inter_corp_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "inter_corps": inter_corp_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        await db.rollback()
        logger.error("Error in get_inter_corp_by_fin", exc_info=True)
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )