from datetime import datetime 
from pydantic import BaseModel

class SignUp(BaseModel):
    name: str
    surname: str
    father_name: str
    fin_kod: str
    email: str
    birth_date: datetime
    password: str

class SignIn(BaseModel):
    fin_kod: str
    password: str

class ResetPassword(BaseModel):
    password: str
    repeated_password: str
    token: str

class VerifyOtpRequest(BaseModel):
    name: str
    surname: str
    father_name: str
    fin_kod: str
    email: str
    birth_date: datetime
    password: str
    otp: int