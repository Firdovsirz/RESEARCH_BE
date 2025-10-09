from sqlalchemy import (
    Integer,
    String,
    Column,
)
from app.db.database import Base

class ExperienceTranslations(Base):
    __tablename__ = "experience_translations"
    id = Column(Integer, primary_key=True, index=True)
    exp_code = Column(String(7), nullable=False)
    lang_code = Column(String(2), nullable=False)
    title = Column(String, nullable=False)
    university = Column(String, nullable=False)


