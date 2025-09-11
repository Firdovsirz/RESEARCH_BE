from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse

class ScopusBase(BaseModel):
    scopus_url: str = Field(..., description="Scopus profile URL")

    @field_validator("scopus_url")
    @classmethod
    def validate_scopus_url(cls, v: str):
        parsed = urlparse(v)
        if not all([parsed.scheme in ("http", "https"), parsed.netloc]):
            raise ValueError("Invalid URL. Must start with http:// or https://")
        if "scopus.com" not in parsed.netloc:
            raise ValueError("URL must be a valid Scopus profile link (contain scopus.com)")
        return v

class ScopusCreate(ScopusBase):
    fin_kod: str = Field(..., min_length=7, max_length=7, description="User FIN code (7 characters)")

class ScopusUpdate(ScopusBase):
    pass

class ScopusOut(ScopusBase):
    id: int
    fin_kod: str

    class Config:
        orm_mode = True
