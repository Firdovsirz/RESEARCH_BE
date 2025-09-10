from app.services.otp import *
from app.db.session import get_db
from app.api.v1.schemas.otp import *
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt_required import token_required

router = APIRouter()

# Send otp to the mail by user's fin kod ("/api/otp/send/{fin_kod}")
# Fin kod pathname

@router.post("/send/{fin_kod}")
async def send_otp_endpoint(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    return await send_otp(fin_kod, db)

# Validate otp by user's fin kod and otp ("/api/otp/validate")
# ValidateOtp schema

@router.post("/validate")
async def validate_otp_endpoint(
    otp_request: ValidateOtp,
    db: AsyncSession = Depends(get_db)
):
    return await validate_otp(otp_request, db)