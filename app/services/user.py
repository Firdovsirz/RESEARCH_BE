import json
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
from app.db.redis_client import get_redis
from fastapi import Depends, status, Query
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.research_areas import ResearchAreas
from app.utils.translator import translate_to_english
from app.models.translations.user_translations import UserTranslations
from app.models.translations.research_areas_translations import ResearchAreasTranslations


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
        
        user.image = user_request.image
        
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
            "scopus": link.scopus_url if link else None,
            "web_of_science": link.webofscience_url if link else None,
            "google_scholar": link.google_scholar_url if link else None,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "scientific_degree_name": user_translation.scientific_degree_name,
            "scientific_name": user_translation.scientific_name,
            "image": user.image,
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
    search: str = Query(None, description="Search term for users and research areas"),
    start: int = Query(0, ge=0),
    end: int = Query(50, ge=1),
    db: AsyncSession = Depends(get_db)
):
    try:
        redis = await get_redis()
        cache_key = f"users:all:{lang_code}:{start}:{end}:{search or 'all'}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            return JSONResponse(
                content=json.loads(cached_data),
                status_code=status.HTTP_200_OK
            )
        
        search_index_key = "users_search_index_minimal"
        search_index_raw = await redis.get(search_index_key)
        if search_index_raw:
            search_index = json.loads(search_index_raw)
        else:
            auth_query = await db.execute(select(Auth))
            auths = auth_query.scalars().all()

            search_index = []
            for auth in auths:
                if not auth.fin_kod:
                    continue

                user_query = await db.execute(select(User).where(User.fin_kod == auth.fin_kod))
                user = user_query.scalar_one_or_none()
                if not user:
                    continue

                user_translations_query = await db.execute(
                    select(UserTranslations).where(UserTranslations.fin_kod == user.fin_kod)
                )
                user_translations = user_translations_query.scalars().all()

                research_areas_query = await db.execute(
                    select(ResearchAreas).where(ResearchAreas.fin_kod == user.fin_kod)
                )
                research_areas = research_areas_query.scalars().all()

                area_codes = [str(ra.area_code) for ra in research_areas if ra.area_code]
                if area_codes:
                    research_areas_translations_query = await db.execute(
                        select(ResearchAreasTranslations).where(
                            ResearchAreasTranslations.area_code.in_(area_codes)
                        )
                    )
                    research_areas_translations = research_areas_translations_query.scalars().all()
                else:
                    research_areas_translations = []

                translations_dict = {ut.language_code: ut for ut in user_translations}

                link_query = await db.execute(select(Links).where(Links.fin_kod == user.fin_kod))
                link = link_query.scalar_one_or_none()

                research_areas_by_lang = {}
                for rat in research_areas_translations:
                    raw_areas = rat.area.split(",")
                    for area in raw_areas:
                        sub_areas = area.split(" and ")
                        for sub_area in sub_areas:
                            sub_area_clean = sub_area.strip()
                            if sub_area_clean:
                                research_areas_by_lang.setdefault(rat.lang_code, []).append(sub_area_clean)

                for lang in translations_dict:
                    translation = translations_dict[lang]
                    user_obj = {
                        "name": user.name or "",
                        "surname": user.surname or "",
                        "fin_kod": user.fin_kod,
                        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                        "email": user.email,
                        "scientific_degree_name": translation.scientific_degree_name or "",
                        "scientific_name": translation.scientific_name or "",
                        "language_code": lang,
                        "research_areas": research_areas_by_lang.get(lang, []),
                        "scopus_url": link.scopus_url if link else "",
                        "webofscience_url": link.webofscience_url if link else "",
                        "google_scholar_url": link.google_scholar_url if link else "",
                        "linkedin_url": link.linkedin_url if link else "",
                        "image": user.image
                    }
                    search_index.append(user_obj)

            await redis.set(search_index_key, json.dumps(search_index), ex=3600)

        # filtered_by_lang = [u for u in search_index if u.get("language_code") == lang_code]

        # Do not filter by language code; include all users regardless of language
        users_to_filter = search_index

        if search:
            search_lower = search.strip().lower()
            def matches_search(u):
                fields = [
                    u.get("name", "").strip().lower(),
                    u.get("surname", "").strip().lower(),
                    u.get("scientific_degree_name", "").strip().lower(),
                    u.get("scientific_name", "").strip().lower(),
                ]
                areas = u.get("research_areas", [])
                fields.extend([area.strip().lower() for area in areas])
                return any(search_lower in field for field in fields)

            filtered = list(filter(matches_search, users_to_filter))
        else:
            filtered = users_to_filter

        total = len(filtered)
        paginated = filtered[start:end]

        if not paginated:
            response_content = {
                "status_code": 204,
                "message": "No content"
            }
            await redis.set(cache_key, json.dumps(response_content), ex=3600)
            return JSONResponse(
                content=response_content,
                status_code=status.HTTP_204_NO_CONTENT
            )

        response_content = {
            "status_code": 200,
            "message": "Users fetched successfully.",
            "total": total,
            "users": paginated
        }
        await redis.set(cache_key, json.dumps(response_content), ex=3600)

        return JSONResponse(
            content=response_content,
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

        if "image" in update_dict:
            user.image = update_dict["image"]

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
