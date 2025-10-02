from pydantic import BaseModel

class CreateWork(BaseModel):
    fin_kod: str
    work_place: str
    duty: str