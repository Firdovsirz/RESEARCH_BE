from pydantic import BaseModel
from typing import List
from datetime import datetime


class PublicationBase(BaseModel):
    fin_kod: str
    publication_code: str

from typing import Optional

class PublicationCreate(BaseModel):
    fin_kod: str
    publication_name: str
    publication_url: Optional[str] = None

class PublicationUpdate(BaseModel):
    publication_name: str
    publication_url: str

class PublicationTranslationResponse(BaseModel):
    lang_code: str
    publication_name: str

    model_config = {
        "from_attributes" : True
    }        

class PublicationResponse(BaseModel):
    id: int
    fin_kod: str
    publication_code: str
    publication_url: str
    translations: List[PublicationTranslationResponse] = [] 
    created_at: datetime

    model_config = {
        "from_attributes" : True
    }








