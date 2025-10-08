from pydantic import BaseModel
from typing import Optional

class CreateEducation(BaseModel):
    start_date: int
    end_date: Optional[int] = None

    class Config:
        orm_mode = True


class EducationResponse(BaseModel):
    edu_code: str
    start_date: int
    end_date: Optional[int]
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True
