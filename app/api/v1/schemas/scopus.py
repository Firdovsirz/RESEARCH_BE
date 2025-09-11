from pydantic import BaseModel, Field

# Shared properties
class ScopusBase(BaseModel):
    scopus_url: str = Field(..., description="Scopus profile URL")

# Schema for creating a new record
class ScopusCreate(ScopusBase):
    fin_kod: str = Field(..., min_length=7, max_length=7, description="User FIN code (7 characters)")

# Schema for updating
class ScopusUpdate(ScopusBase):
    pass  # You can add optional fields here later

# Schema for reading (response)
class ScopusOut(ScopusBase):
    id: int
    fin_kod: str

    class Config:
        orm_mode = True  
