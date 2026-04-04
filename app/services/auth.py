import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.auth import ResetPassword, SignIn, SignUp, VerifyOtpRequest
from app.db.database import get_db
from app.models.auth import Auth
from app.models.otp import Otp
from app.models.user import User
from app.services.otp import check_otp_validity
from app.utils.email import send_html_email
from app.utils.jwt import encode_auth_token, decode_otp_token
from app.utils.otp import generateOtp
from app.utils.password import hash_password, verify_password, validate_password

templates = Jinja2Templates(directory="templates")

async def signup(
    signup_request: SignUp,
    db: AsyncSession
) -> JSONResponse:
    query_result = await db.execute(
        select(Auth)
        .where(
            or_(
                Auth.fin_kod == signup_request.fin_kod,
                Auth.email == signup_request.email
            )
        )
    )

    auth_user = query_result.scalar_one_or_none()

    if auth_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    await validate_password(signup_request.password)

    otp = await generateOtp()
    hashed_otp = hash_password(otp)

    new_otp = Otp(
        fin_kod=signup_request.fin_kod,
        otp=hashed_otp,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(new_otp)
    await db.commit()
    
    subject = "OTP"

    try:
        html_content = templates.get_template("/email/otp_verification.html").render({
            "name": signup_request.name,
            "otp_code": otp
        })
        send_html_email(subject, signup_request.email, signup_request.name, html_content)
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        # We don't necessarily want to fail the whole signup if email fails, 
        # but in this case OTP is required to proceed.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email"
        )

    return JSONResponse(
        content={
            "status_code": 200,
            "message": "OTP sent successfully."
        }, status_code=status.HTTP_200_OK
    )

async def verify_signup(
    otp_request: VerifyOtpRequest,
    db: AsyncSession
) -> JSONResponse:
    if not await check_otp_validity(otp_request.fin_kod, otp_request.otp, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid otp"
        )

    # Check if user already exists again to be safe
    query_result = await db.execute(select(Auth).where(Auth.fin_kod == otp_request.fin_kod))
    if query_result.scalar_one_or_none():
         raise HTTPException(status_code=409, detail="User already registered")

    hashed_password = hash_password(otp_request.password)

    new_auth = Auth(
        fin_kod=otp_request.fin_kod,
        email=otp_request.email,
        password=hashed_password,
        created_at=datetime.utcnow(),
        approved=False # Default is False anyway
    )

    birth_date_naive = otp_request.birth_date
    if birth_date_naive.tzinfo is not None:
        birth_date_naive = birth_date_naive.replace(tzinfo=None)

    new_user = User(
        fin_kod=otp_request.fin_kod,
        name=otp_request.name,
        surname=otp_request.surname,
        father_name=otp_request.father_name,
        email=otp_request.email,
        birth_date=birth_date_naive,
        created_at=datetime.utcnow()
    )
    db.add(new_auth)
    db.add(new_user)

    await db.commit()

    return JSONResponse(
        content={
            "status_code": 201,
            "message": "User registered successfully, waiting for approval."
        }, status_code=status.HTTP_201_CREATED
    )

async def signin(
    signin_request: SignIn,
    db: AsyncSession
) -> JSONResponse:
    query_result = await db.execute(
        select(Auth).where(Auth.fin_kod == signin_request.fin_kod)
    )
    auth_user = query_result.scalar_one_or_none()

    if not auth_user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not auth_user.approved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not approved yet"
        )
    
    if not verify_password(signin_request.password, auth_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    query_user = await db.execute(
        select(User).where(User.fin_kod == signin_request.fin_kod)
    )
    user = query_user.scalar_one_or_none()

    token = encode_auth_token(auth_user.fin_kod, auth_user.role, True)
    
    return JSONResponse(
        content={
            "status_code": 200,
            "message": "AUTHORIZED",
            "data": {
                "token": token,
                "user": {
                    "name": user.name,
                    "surname": user.surname,
                    "father_name": user.father_name,
                    "fin_kod": user.fin_kod,
                    "email": user.email,
                    "role": auth_user.role,
                    "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                }
            }
        }, status_code=status.HTTP_200_OK
    )

async def reset_password(
    reset_request: ResetPassword,
    db: AsyncSession
) -> JSONResponse:
    encoded_data = decode_otp_token(reset_request.token)

    query_result = await db.execute(
        select(Auth).where(Auth.fin_kod == encoded_data['fin_kod'])
    )
    user = query_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if reset_request.password != reset_request.repeated_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if verify_password(reset_request.password, user.password):
        raise HTTPException(status_code=400, detail="New password must be different from the old one")

    user.password = hash_password(reset_request.password)
    user.updated_at = datetime.utcnow()
    await db.commit()

    return JSONResponse(
        content={
            "status_code": 200,
            "message": "Password reset successfully."
        },
        status_code=status.HTTP_200_OK
    )

async def approve_user(
    fin_kod: str,
    db: AsyncSession
) -> JSONResponse:
    user_query = await db.execute(
        select(Auth).where(Auth.fin_kod == fin_kod)
    )
    auth_user = user_query.scalar_one_or_none()

    if not auth_user:
        raise HTTPException(status_code=404, detail="User not found")

    if auth_user.approved:
        raise HTTPException(status_code=409, detail="User already approved")
    
    auth_user.approved = True
    auth_user.updated_at = datetime.utcnow()

    await db.commit()

    return JSONResponse(
        content={
            "status_code": 200,
            "message": "User approved successfully."
        }, status_code=status.HTTP_200_OK
    )

async def reject_user(
    fin_kod: str,
    db: AsyncSession
) -> JSONResponse:
    auth_user_query = await db.execute(
        select(Auth).where(Auth.fin_kod == fin_kod)
    )
    auth_user = auth_user_query.scalar_one_or_none()

    if not auth_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_query = await db.execute(
        select(User).where(User.fin_kod == fin_kod)
    )
    user = user_query.scalar_one_or_none()

    if user:
        await db.delete(user)
    
    await db.delete(auth_user)
    await db.commit()

    return JSONResponse(
        content={
            "status_code": 200,
            "message": "User rejected successfully."
        }, status_code=status.HTTP_200_OK
    )

async def get_app_waiting_users(
    db: AsyncSession
) -> JSONResponse:
    auth_query = await db.execute(
        select(Auth).where(Auth.approved == False)
    )
    auth_users = auth_query.scalars().all()

    if not auth_users:
        return JSONResponse(
            content={"status_code": 204, "message": "No pending users"}, 
            status_code=status.HTTP_200_OK # 204 has no body, but here we might want to return a message
        )
    
    users_arr = []
    for auth_user in auth_users:
        user_query = await db.execute(
            select(User).where(User.fin_kod == auth_user.fin_kod)
        )
        user = user_query.scalar_one_or_none()

        if user:
            users_arr.append({
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "father_name": user.father_name,
                "email": user.email,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
    
    return JSONResponse(
        content={
            "status_code": 200,
            "message": "Pending users fetched successfully.",
            "users": users_arr
        }
    )
