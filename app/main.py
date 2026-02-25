from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from app.utils.log_middleware import log_requests
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

import os
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

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

app = FastAPI(
    title="AzTU Research",
    version="1.0.0",
    description="Backend for AZTU Research admin dashboard."
)

log_requests(app)

# load api key

app.state.check_api_key = os.getenv("API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://researchers.aztu.edu.az", "http://localhost:5173", "http://researcher.karamshukurlu.site"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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




from fastapi import Depends
from app.utils.api_key_checker import check_api_key

@app.get("/check-api-key")
async def check_api_key_route(api_key: str = Depends(check_api_key)):
    return {"message": "API key is valid!", "api_key": api_key}

app.mount("/static", StaticFiles(directory="static"), name="static")