import logging
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.otp import ValidateOtp
from app.db.database import get_db
from app.models.otp import Otp
from app.models.user import User
from app.utils.email import send_html_email
from app.utils.jwt import encode_otp_token
from app.utils.otp import generateOtp
from app.utils.password import hash_password, verify_password

templates = Jinja2Templates(directory="templates")

async def check_otp_validity(fin_kod: str, otp_code: int, db: AsyncSession) -> bool:
    """Helper function to check if an OTP is valid and not expired."""
    otp_query = await db.execute(
        select(Otp).where(Otp.fin_kod == fin_kod)
    )
    user_otp = otp_query.scalar_one_or_none()

    if not user_otp:
        return False
    
    if not verify_password(str(otp_code), user_otp.otp):
        return False
    
    if user_otp.expires_at < datetime.utcnow():
        return False
    
    # Optional: Delete OTP after successful verification here or in the caller
    # For now, we'll let the caller decide if it wants to delete it.
    return True

async def send_otp(
    fin_kod: str,
    db: AsyncSession
) -> JSONResponse:
    query_result = await db.execute(
        select(User).where(User.fin_kod == fin_kod)
    )
    user = query_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Fin kod is not valid.")
    
    otp_query = await db.execute(
        select(Otp).where(Otp.fin_kod == fin_kod)
    )
    previous_otp = otp_query.scalar_one_or_none()

    if previous_otp:
        # Instead of 409, we might want to update or allow resending
        # For now, following original logic but raising HTTPException
        raise HTTPException(status_code=409, detail="OTP already exists for this user.")
    
    otp = await generateOtp()
    hashed_otp = hash_password(otp)

    new_otp = Otp(
        fin_kod=fin_kod,
        otp=hashed_otp,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(new_otp)
    await db.commit()
    
    try:
        html_content = templates.get_template("/email/otp_verification.html").render({
            "name": user.name,
            "otp_code": otp
        })
        send_html_email("OTP", user.email, user.name, html_content)
    except Exception as e:
        logging.error(f"Failed to send OTP email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return JSONResponse(
        content={
            "status_code": 200,
            "message": "OTP sent successfully."
        }, status_code=status.HTTP_200_OK
    )

async def validate_otp_service(
    otp_request: ValidateOtp,
    db: AsyncSession
) -> JSONResponse:
    """Service to validate OTP and return a token."""
    query_result = await db.execute(
        select(User).where(User.fin_kod == otp_request.fin_kod)
    )
    user = query_result.scalar_one_or_none()

    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    
    if not await check_otp_validity(otp_request.fin_kod, otp_request.otp, db):
         raise HTTPException(status_code=401, detail="OTP is invalid or expired.")
    
    token = encode_otp_token(otp_request.fin_kod, otp_request.otp)

    # Delete OTP after validation
    otp_query = await db.execute(select(Otp).where(Otp.fin_kod == otp_request.fin_kod))
    user_otp = otp_query.scalar_one_or_none()
    if user_otp:
        await db.delete(user_otp)
        await db.commit()
    
    return JSONResponse(
        content={
            "status_code": 200,
            "message": "Otp validated successfully.",
            "token": token
        }
    )
