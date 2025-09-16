from pydantic import BaseModel
from typing import List

class LanguageBase(BaseModel):
    code: str
    name: str

class LanguageOut(LanguageBase):
    class Config:
        orm_mode = True

class UserLanguagesRequest(BaseModel):
    user_id: int
    languages: List[str]  # ISO language codes

class UserLanguagesResponse(BaseModel):
    user_id: int
    languages: List[LanguageOut]