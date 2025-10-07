from typing import Optional
from pydantic import BaseModel

class CreateInterCoor(BaseModel):
    fin_kod: str
    inter_coor_name: str
    name: Optional[str] = None 
    surname: Optional[str] = None
    email: Optional[str] = None
    image: Optional[str] = None