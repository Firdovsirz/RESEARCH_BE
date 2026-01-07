from typing import Optional
from typing import Annotated
from pydantic import BaseModel, constr

NonEmptyStr = Annotated[str, constr(min_length=1)]

class CreateEducation(BaseModel):
    fin_kod: NonEmptyStr
    title: NonEmptyStr
    university: NonEmptyStr
    start_date: int
    end_date: Optional[int] = None

    class Config:
        orm_mode = True


class EducationResponse(BaseModel):
    edu_code: str
    start_date: int
    end_date: Optional[int] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True