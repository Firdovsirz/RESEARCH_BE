from pydantic import BaseModel
from typing import Optional
class CreateInterCoor(BaseModel):
    fin_kod: str
    inter_coor_name: str
    name: str 
    surname: str
    email:str
    image: Optional[str] = None