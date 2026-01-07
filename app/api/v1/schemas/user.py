from typing import Optional
from pydantic import BaseModel

class CreateUser(BaseModel):
    fin_kod: str
    scientific_degree_name: str
    scientific_name: str
    bio: str
    image: Optional[str] = None

class UpdateUser(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    father_name: Optional[str] = None
    email: Optional[str] = None
    image: Optional[str] = None
    scientific_degree_name: Optional[str] = None
    scientific_name: Optional[str] = None
    bio: Optional[str] = None
