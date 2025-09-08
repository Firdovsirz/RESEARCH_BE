from sqlalchemy import or_
from app.utils.otp import *
from app.utils.email import *
from app.models.otp import Otp
from app.models.user import User
from app.utils.password import *
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from app.utils.jwt import encode_otp_token
from fastapi.templating import Jinja2Templates
from app.api.v1.schemas.otp import ValidateOtp
from sqlalchemy.ext.asyncio import AsyncSession