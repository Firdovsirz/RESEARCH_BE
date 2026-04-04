import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.log_middleware import LogRequestsMiddleware
from app.db.redis_client import redis_manager
from app.utils.api_key_checker import check_api_key

# Routes
from app.api.v1.routes.cv import router as cv_router
from app.api.v1.routes.bio import router as bio_router
from app.api.v1.routes.logs import router as log_router
from app.api.v1.routes.work import router as work_router
from app.api.v1.routes.user import router as user_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.links import router as links_router
from app.api.v1.routes.article import router as article_router
from app.api.v1.routes.language import router as language_router
from app.api.v1.routes.research_areas import router as area_router
from app.api.v1.routes.education import router as education_router
from app.api.v1.routes.experience import router as experience_router
from app.api.v1.routes.inter_corp import router as inter_corp_router
from app.api.v1.routes.publication import router as publication_router
from app.api.v1.routes.scientific_name import router as scientific_name_router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Redis
    await redis_manager.connect()
    yield
    # Shutdown: Close Redis
    await redis_manager.disconnect()

app = FastAPI(
    title="AzTU Research",
    version="1.0.0",
    description="Backend for AZTU Research admin dashboard.",
    lifespan=lifespan
)

# Configuration
app.state.check_api_key = os.getenv("API_KEY")
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "https://researchers.aztu.edu.az,http://localhost:5173,http://researchers.karamshukurlu.site")
allowed_origins = [o.strip() for o in allowed_origins_str.split(",") if o.strip()]

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status_code": 422, "message": "Validation Error", "details": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status_code": 500, "message": "Internal Server Error", "error": str(exc)},
    )

# Middlewares
app.add_middleware(LogRequestsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(cv_router, prefix="/api/cv", tags=["CV"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(log_router, prefix="/api/log", tags=["LOG"])
app.include_router(links_router, prefix="/api/link", tags=["Links"])
app.include_router(bio_router, prefix="/api/bio", tags=["Bio"])
app.include_router(user_router, prefix="/api/user", tags=["User"])
app.include_router(work_router, prefix="/api/work", tags=["Work"])
app.include_router(article_router, prefix="/api/article", tags=["Article"])
app.include_router(language_router, prefix="/api/language", tags=["Language"])
app.include_router(education_router, prefix="/api/education", tags=["Education"])
app.include_router(area_router, prefix="/api/research-area", tags=["Research Area"])
app.include_router(experience_router, prefix="/api/experience", tags=["Experience"])
app.include_router(publication_router, prefix="/api/publication", tags=["Publication"])
app.include_router(scientific_name_router, prefix="/api/scientific_name", tags=["ScientificName"])
app.include_router(inter_corp_router, prefix="/api/inter-corp", tags=["International Coorperation"])

@app.get("/check-api-key")
async def check_api_key_route(api_key: str = Depends(check_api_key)):
    return {"message": "API key is valid!", "api_key": api_key}

app.mount("/static", StaticFiles(directory="static"), name="static")
