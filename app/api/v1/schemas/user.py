from typing import Optional
from pydantic import BaseModel

class UpdateUser(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    father_name: Optional[str] = None
    email: Optional[str] = None