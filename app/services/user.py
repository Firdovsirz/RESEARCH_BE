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
from app.api.v1.schemas.user import UpdateUser
from sqlalchemy.ext.asyncio import AsyncSession

# Update user data (patch)
# One of these columns name, surname, father_name, email

async def update_user(
    fin_kod: str,
    update_data: UpdateUser,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        user_query = await db.execute(
            select(User)
            .where(User.fin_kod == fin_kod)
        )
        user = user_query.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "User not found"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        update_dict = update_data.dict(exclude_unset=True)

        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "User updated successfully."
            }, status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )