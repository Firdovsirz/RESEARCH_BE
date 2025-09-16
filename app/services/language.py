import pycountry
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.language import Language
from app.api.v1.schemas.language import UserLanguagesRequest


def get_all_languages():
    """Return all available languages (for dropdown)."""
    languages = []
    for lang in pycountry.languages:
        if hasattr(lang, "alpha_2"):  # only ISO 639-1 languages
            languages.append({"code": lang.alpha_2, "name": lang.name})
    return languages


def save_user_languages(db: Session, data: UserLanguagesRequest):
    """Save selected languages for a specific user."""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Valid ISO codes
    valid_codes = {lang.alpha_2 for lang in pycountry.languages if hasattr(lang, "alpha_2")}
    for code in data.languages:
        if code not in valid_codes:
            raise HTTPException(status_code=400, detail=f"Invalid language code: {code}")

    langs = []
    for code in data.languages:
        lang = db.query(Language).filter(Language.code == code).first()
        if not lang:
            py_lang = pycountry.languages.get(alpha_2=code)
            lang = Language(code=code, name=py_lang.name)
            db.add(lang)
        langs.append(lang)

    # Assign languages to user
    user.languages = langs
    db.commit()
    db.refresh(user)
    return user


def get_user_languages(db: Session, user_id: int):
    """Get all languages saved by a specific user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user