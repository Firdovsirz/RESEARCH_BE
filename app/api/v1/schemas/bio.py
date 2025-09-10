from pydantic import BaseModel
from typing import List
from datetime import datetime


class BioBase(BaseModel):
    fin_kod: str
    bio_code: str

class BioCreate(BioBase):
    bio_field: str

class BioUpdate(BaseModel):
    bio_field: str

class BioTranslationResponse(BaseModel):
    lang_code: str
    bio_field: str

    model_config = {
        "from_attributes" : True
    }        

class BioResponse(BaseModel):
    id: int
    fin_kod: str
    bio_code: str
    translations: List[BioTranslationResponse] = [] 
    created_at: datetime

    model_config = {
        "from_attributes" : True
    }








