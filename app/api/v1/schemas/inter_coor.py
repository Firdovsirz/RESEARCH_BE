from pydantic import BaseModel

class CreateInterCoor(BaseModel):
    fin_kod: str
    inter_coor_name: str