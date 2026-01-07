import logging
from sqlalchemy import or_
from app.utils.jwt import *
from app.utils.otp import *
from app.utils.email import *
from app.models.otp import Otp
from app.models.auth import Auth
from app.models.user import User
from app.utils.password import *
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.api.v1.schemas.auth import *
from app.utils.otp import generateOtp
from datetime import datetime, timedelta
from app.services.otp import validate_otp
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

templates = Jinja2Templates(directory="templates")

# Register a new user by validating input, check duplicates
# Hashing the password, creating Auth and User records
# Send otp to the email using email util, with otp_template

async def signup(
    signup_request: SignUp,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
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
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "User already exists"
                }, status_code=status.HTTP_409_CONFLICT
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
        await db.refresh(new_otp)
        
        subject = "OTP"

        html_content = templates.get_template("/email/otp_verification.html").render({
            "name": signup_request.name,
            "otp_code": otp
        })

        send_html_email(subject, signup_request.email, signup_request.name, html_content)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "OTP sent successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        logging.exception("Error during signup")
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# verify signup with otp
# validate otp and save user records

async def verify_signup(
    otp_request: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db)
):
    try:

        if not validate_otp(otp_request.fin_kod, otp_request.otp):
            return JSONResponse(
                content={
                    "statusCode": 401,
                    "message": "Invalid otp"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )

        hashed_password = hash_password(otp_request.password)

        new_auth = Auth(
            fin_kod=otp_request.fin_kod,
            email=otp_request.email,
            password=hashed_password,
            created_at=datetime.utcnow()
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
        await db.refresh(new_auth)
        await db.refresh(new_user)

        return JSONResponse(
            content={
                "status_code": 201,
                "message": "OTP sent successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        logging.exception("Error during signin")
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Login user by fin_kod and password
# Check password using verify_password from password util
# Return token and user details

async def signin(
    signin_request: SignIn,
    db: AsyncSession = Depends(get_db) 
) -> JSONResponse:
    try:
        query_result = await db.execute(
            select(Auth)
            .where(
                Auth.fin_kod == signin_request.fin_kod
            )
        )

        auth_user = query_result.scalar_one_or_none()

        query_user = await db.execute(
            select(User)
            .where(
                User.fin_kod == signin_request.fin_kod
            )
        )

        user = query_user.scalar_one_or_none()

        if not auth_user or not auth_user.approved:
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if not verify_password(signin_request.password, auth_user.password):
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
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
    
    except Exception as e:
        logging.exception("Error during signin")
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Reset password by token and fin_kod from user
# Encode the token to verify user data
# Get new_password from user and validate

async def reset_password(
    reset_request: ResetPassword,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        try:
            encoded_data = decode_otp_token(reset_request.token)
        except HTTPException as e:
            return JSONResponse(
                content={
                    "status_code": e.status_code,
                    "message": e.detail
                },
                status_code=e.status_code
            )

        if hasattr(reset_request, 'otp') and reset_request.otp != encoded_data.get('otp'):
            return JSONResponse(
                content={
                    "status_code": 401,
                    "message": "OTP is invalid"
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        query_result = await db.execute(
            select(Auth).where(Auth.fin_kod == encoded_data['fin_kod'])
        )
        user = query_result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        if reset_request.password != reset_request.repeated_password:
            return JSONResponse(
                content={
                    "status_code": 400,
                    "message": "Password and repeated password do not match"
                }, status_code=status.HTTP_400_BAD_REQUEST
            )

        if verify_password(reset_request.password, user.password):
            return JSONResponse(
                content={
                    "status_code": 400,
                    "message": "New password must be different from the old one"
                }, status_code=status.HTTP_400_BAD_REQUEST
            )

        user.password = hash_password(reset_request.password)
        await db.commit()
        await db.refresh(user)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Password reset successfully."
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Approve user by admin
# Update the approved column in auth table to True

async def approve_user(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == fin_kod)
        )

        auth_user = user_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        if str(auth_user.approved).lower() in ["true", "1"]:
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "User already approved"
                }, status_code=status.HTTP_409_CONFLICT
            )
        
        auth_user.approved = True

        await db.commit()
        await db.refresh(auth_user)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "User approved successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Reject user by admin
# Delete user records from auth and user table

async def reject_user(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_user_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == fin_kod)
        )
        user_query = await db.execute(
            select(User)
            .where(User.fin_kod == fin_kod)
        )

        user = user_query.scalar_one_or_none()

        auth_user = auth_user_query.scalar_one_or_none()

        if not auth_user or not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found."
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        await db.delete(auth_user)
        await db.delete(user)
        await db.commit()

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "User rejected successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_app_waiting_users(
    db: AsyncSession = Depends(get_db)
):
    try:
        
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.approved == "false")
        )

        auth_users = auth_query.scalars().all()

        if not auth_users:
            return JSONResponse(
                content={
                    "status_code": 204
                }, status_code=204
            )
        
        users_arr = []
        
        for auth_user in auth_users:

            user_query = await db.execute(
                select(User)
                .where(User.fin_kod == auth_user.fin_kod)
            )

            user = user_query.scalar_one_or_none()

            user_obj = {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "father_name": user.father_name,
                "email": user.email,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }

            users_arr.append(user_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Approve waiting users fetched successfully.",
                "users": users_arr
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def reject_user(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        auth_query = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == fin_kod)
        )

        auth_user = auth_query.scalar_one_or_none()

        if not auth_user:
            return JSONResponse(
                content={
                    "status_code": 204
                }, status_code=204
            )
        
        user_query = await db.execute(
            select(User)
            .where(User.fin_kod == fin_kod)
        )

        user = user_query.scalar_one_or_none()

        if user:
            await db.delete(user)
        
        await db.delete(auth_user)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "User not found."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "message": "Internal Error"
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )