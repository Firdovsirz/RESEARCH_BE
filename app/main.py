from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

import os
from app.api.v1.routes.cv import router as cv_router
from app.api.v1.routes.otp import router as otp_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.article import router as article_router
from app.api.v1.routes.bio import router as bio_router
from app.api.v1.routes.scientific_name import router as scientific_name_router
from app.api.v1.routes.publication import router as publication_router

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

app = FastAPI(
    title="AzTU Research",
    version="1.0.0",
    description="Backend for AZTU Research admin dashboard."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv_router, prefix="/api", tags=["CV"])
app.include_router(otp_router, prefix="/api", tags=["OTP"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(article_router, prefix="/api/article", tags=["Article"])
app.include_router(bio_router, prefix="/api/bio", tags=["Bio"])
app.include_router(scientific_name_router, prefix="/api/scientific_name", tags=["ScientificName"])
app.include_router(publication_router, prefix="/api/publication", tags=["Publication"])

@app.get("/")
def read_root():
    return {"message": "AzTU research"}