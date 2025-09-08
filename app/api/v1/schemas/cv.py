from pydantic import BaseModel
from fastapi import UploadFile, Form, File

class CreateCv(BaseModel):
    fin_kod: str
    cv: UploadFile

    @classmethod
    def as_form(
        cls,
        fin_kod: str = Form(...),
        cv: UploadFile = File(...)
    ):
        return cls(fin_kod=fin_kod, cv=cv)