from pydantic import BaseModel
from typing import List
from datetime import datetime


class ScientificNameBase(BaseModel):
    fin_kod: str
    scientific_name_code: int

class ScientificNameCreate(ScientificNameBase):
    scientific_name: str

class ScientificNameUpdate(BaseModel):
    scientific_name: str

class ScientificNameTranslationResponse(BaseModel):
    lang_code: str
    scientific_name: str

    model_config = {
        "from_attributes" : True
    }        

class ScientificNameResponse(BaseModel):
    id: int
    fin_kod: str
    scientific_name_code: int
    translations: List[ScientificNameTranslationResponse] = [] 
    created_at: datetime

    model_config = {
        "from_attributes" : True
    }








