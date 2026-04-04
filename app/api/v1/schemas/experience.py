from pydantic import BaseModel
from typing import Optional

class CreateExperience(BaseModel):
    fin_kod: str
    title: str
    university: str
    start_date: int
    end_date: Optional[int] = None

    class Config:
        from_attributes = True


class ExperienceResponse(BaseModel):
    exp_code: str
    start_date: int
    end_date: Optional[int]
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
