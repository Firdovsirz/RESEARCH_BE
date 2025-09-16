from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import language as user_languages_service
from app.api.v1.schemas.language import UserLanguagesRequest, UserLanguagesResponse


router = APIRouter()


@router.get("/languages")
def get_languages():
    return {"languages": user_languages_service.get_all_languages()}


@router.post("/languages", response_model=UserLanguagesResponse)
def add_languages(data: UserLanguagesRequest, db: Session = Depends(get_db)):
    user = user_languages_service.save_user_languages(db, data)
    return {"user_id": user.id, "languages": user.languages}


@router.get("/{user_id}/languages", response_model=UserLanguagesResponse)
def get_user_languages(user_id: int, db: Session = Depends(get_db)):
    user = user_languages_service.get_user_languages(db, user_id)
    return {"user_id": user.id, "languages": user.languages}