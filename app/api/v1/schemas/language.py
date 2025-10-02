from pydantic import BaseModel

class CreateLanguage(BaseModel):
    fin_kod: str
    language_short_name: str
    language_name: str
    language_level: str