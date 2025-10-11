from pydantic import BaseModel
from typing import List
from datetime import datetime

class CreateArea(BaseModel):
    fin_kod: str
    research_area: str