from typing import Optional
from pydantic import BaseModel

class CreateUser(BaseModel):
    fin_kod: str
    scientific_degree_name: str
    scientific_name: str
    bio: str

class UpdateUser(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    father_name: Optional[str] = None
    email: Optional[str] = None
