from typing import Optional
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse

class LinksBase(BaseModel):
    scopus_url: Optional[str] = None
    webofscience_url: Optional[str] = None
    google_scholar_url: Optional[str] = None
    linkedin_url: Optional[str] = None

    @field_validator("scopus_url")
    @classmethod
    def validate_scopus_url(cls, v: str):
        parsed = urlparse(v)
        
        if parsed.scheme != "https":
            raise ValueError("Invalid URL. Must start with https://")

        if not any(domain in parsed.netloc for domain in ["scopus.com", "webofscience.com", "scholar.google.com", "linkedin.com"]):
            raise ValueError(
                "URL must be a valid Scopus, Web of Science, Google Scholar, or LinkedIn profile link "
                "(contain scopus.com, webofscience.com, scholar.google.com, or linkedin.com in the domain)."
            )

        return v

class LinksCreate(LinksBase):
    fin_kod: str = Field(..., min_length=6, max_length=7, description="User FIN code (6(for foreign persons) or 7 characters)")

class LinksUpdate(LinksBase):
    pass

class LinksOut(LinksBase):
    id: int
    fin_kod: str

    class Config:
        orm_mode = True
