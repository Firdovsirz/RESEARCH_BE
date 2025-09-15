from pydantic import BaseModel
from typing import List
from datetime import datetime


class ArticleBase(BaseModel):
    fin_kod: str
    article_code: str

class ArticleCreate(ArticleBase):
    article_field: str

class ArticleUpdate(BaseModel):
    article_field: str

class ArticleTranslationResponse(BaseModel):
    lang_code: str
    article_field: str

    model_config = {
        "from_attributes" : True
    }        

class ArticleResponse(BaseModel):
    id: int
    fin_kod: str
    article_code: str
    translations: List[ArticleTranslationResponse] = [] 
    created_at: datetime

    model_config = {
        "from_attributes" : True
    }








