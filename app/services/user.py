from sqlalchemy import or_
from app.utils.otp import *
from app.utils.email import *
from datetime import datetime
from app.models.user import User
from app.models.auth import Auth
from app.utils.password import *
from app.db.session import get_db
from app.models.links import Links
from sqlalchemy.future import select
from app.api.v1.schemas.user import *
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.models.translations.user_translations import UserTranslations

# Create user translations by CreateUser schema
# translate details using trasnslator util

async def create_user(
    user_request: CreateUser,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == user_request.fin_kod)
        )

        auth_user = auth_query.scalar_one_or_none()

        user_query = await db.execute(
            select(User)
            .where(User.fin_kod == user_request.fin_kod)
        )

        user = user_query.scalar_one_or_none()

        user_translation_query = await db.execute(
            select(UserTranslations)
            .where(UserTranslations.fin_kod == user_request.fin_kod)
        )

        user_translation = await db.execute(
            select(UserTranslations).where(UserTranslations.fin_kod == user_request.fin_kod).limit(1)
        )
        if user_translation.scalar_one_or_none():
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "User details already exists."
                }, status_code=status.HTTP_409_CONFLICT
            )

        if not auth_user or not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Fin kod is not valid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        new_user_az = UserTranslations(
            language_code="az",
            fin_kod=user_request.fin_kod,
            scientific_degree_name=user_request.scientific_degree_name,
            scientific_name=user_request.scientific_name,
            bio=user_request.bio,
            created_at=datetime.utcnow()
        )

        new_user_en = UserTranslations(
            language_code="en",
            fin_kod=user_request.fin_kod,
            scientific_degree_name=translate_to_english(user_request.scientific_degree_name),
            scientific_name=translate_to_english(user_request.scientific_name),
            bio=translate_to_english(user_request.bio),
            created_at=datetime.utcnow()
        )

        db.add(new_user_az)
        db.add(new_user_en)
        await db.commit()
        await db.refresh(new_user_az)
        await db.refresh(new_user_en)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "User details added successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_profile(
    fin_kod: str,
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = await db.execute(
            select(User)
            .where(User.fin_kod == fin_kod)
        )

        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Fin kod is not valid"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        user_translation_query = await db.execute(
            select(UserTranslations)
            .where(
                UserTranslations.fin_kod == fin_kod,
                UserTranslations.language_code == lang_code
            )
        )

        user_translation = user_translation_query.scalar_one_or_none()

        link_query = await db.execute(
            select(Links)
            .where(Links.fin_kod == fin_kod)
        )
        
        link = link_query.scalar_one_or_none()

        user_details = {
            "name": user.name,
            "surname": user.surname,
            "father_name": user.father_name,
            "fin_kod": user.fin_kod,
            "email": user.email,
            "scopus": link.scopus_url,
            "web_of_science": link.webofscience_url,
            "google_scholar": link.google_scholar_url,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "scientific_degree_name": user_translation.scientific_degree_name,
            "scientific_name": user_translation.scientific_name,
            "bio": user_translation.bio,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "User details fetched successfully",
                "user": user_details
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_all_users(
    lang_code: str = Depends(get_language),
    start: int = Query(0, ge=0),
    end: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get total number of users with role 2
        total_query = await db.execute(select(Auth).where(Auth.role == 2))
        total_auths = total_query.scalars().all()
        total = len(total_auths)

        # Get paginated users
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.role == 2)
            .offset(start)
            .limit(end - start)
        )
        auths = auth_query.scalars().all()

        if not auths:
            return JSONResponse(
                content={
                    "status_code": 204,
                    "message": "No content"
                },
                status_code=status.HTTP_204_NO_CONTENT
            )

        users_list = []

        for auth in auths:
            if not auth.fin_kod:
                continue

            # Fetch the User
            user_query = await db.execute(select(User).where(User.fin_kod == auth.fin_kod))
            user = user_query.scalar_one_or_none()
            if not user:
                continue

            # Fetch the translation
            user_translation_query = await db.execute(
                select(UserTranslations)
                .where(
                    UserTranslations.fin_kod == user.fin_kod,
                    UserTranslations.language_code == lang_code
                )
            )
            user_translation = user_translation_query.scalar_one_or_none()

            # Safely get translation fields
            scientific_degree_name = user_translation.scientific_degree_name if user_translation else None
            scientific_name = user_translation.scientific_name if user_translation else None
            bio = user_translation.bio if user_translation else None

            # Build user object
            user_obj = {
                "name": user.name,
                "surname": user.surname,
                "father_name": user.father_name,
                "email": user.email,
                "bio": bio,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "scientific_degree_name": scientific_degree_name,
                "scientific_name": scientific_name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }

            users_list.append(user_obj)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Users fetched successfully.",
                "total": total,
                "users": users_list
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Update user data (patch)
# One of these columns name, surname, father_name, email

async def update_user(
    fin_kod: str,
    update_data: UpdateUser,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        user_query = await db.execute(
            select(User)
            .where(User.fin_kod == fin_kod)
        )
        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        update_dict = update_data.dict(exclude_unset=True)

        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "User updated successfully."
            }, status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )