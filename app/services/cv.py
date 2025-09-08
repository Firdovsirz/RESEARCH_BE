import os
from fastapi import status
from fastapi import Depends
from app.models.cv import Cv
from datetime import datetime
from app.models.user import User
from app.db.session import get_db
from sqlalchemy.future import select
from app.api.v1.schemas.cv import CreateCv
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Add cv for user upload cv as a file
# Cv will be saved in /stativc/cv/ path with /{fin_kod} folder and the name /{fin_kod}/CV_{fin_kod}_{current_year}

async def add_cv(
    cv_request: CreateCv = Depends(CreateCv.as_form),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        query_result = await db.execute(
            select(User).where(User.fin_kod == cv_request.fin_kod)
        )
        user = query_result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": "Fin kod is not valid."
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        user_folder = os.path.join("static", "cv", cv_request.fin_kod)
        if os.path.exists(user_folder):
            return JSONResponse(
                content={
                    "status_code": 409,
                    "message": "CV folder for this fin_kod already exists."
                },
                status_code=status.HTTP_409_CONFLICT
            )

        os.makedirs(user_folder, exist_ok=True)

        current_year = datetime.utcnow().year
        filename = f"CV_{cv_request.fin_kod}_{current_year}{os.path.splitext(cv_request.cv.filename)[1]}"
        save_path = os.path.join(user_folder, filename)

        with open(save_path, "wb") as f:
            f.write(await cv_request.cv.read())

        new_cv = Cv(
            fin_kod=cv_request.fin_kod,
            cv_path=save_path,
            created_at=datetime.utcnow()
        )
        db.add(new_cv)
        await db.commit()
        await db.refresh(new_cv)

        return JSONResponse(
            content={"status_code": 201, "message": "CV uploaded successfully."},
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return JSONResponse(
            content={"status_code": 500, "message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Get cv by user's fin kod
# Return cv if the cv is available in /static/cv/{fin_kod}/CV_{fin_kod}_{current_year} path

async def get_cv(
    fin_kod: str,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        folder_path = os.path.join("static", "cv", fin_kod)
        if not os.path.isdir(folder_path):
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": f"CV folder not found for fin_kod {fin_kod}"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        result = await db.execute(select(Cv).where(Cv.fin_kod == fin_kod))
        cv_record = result.scalar_one_or_none()

        if not cv_record:
            return JSONResponse(
                content={
                    "status_code": 404,
                    "message": f"No CV found in database for fin_kod {fin_kod}"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        return JSONResponse(
            content={
                "status_code": 200,
                "cv_path": cv_record.cv_path
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "message": f"Internal server error: {str(e)}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )