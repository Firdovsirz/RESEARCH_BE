from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class EducationTranslation(Base):
    __tablename__ = "education_translations"
    id = Column(Integer, primary_key=True, index=True)
    edu_code = Column(String(7), nullable=False)
    lang_code = Column(String(2), nullable=False)
    tittle = Column(String(255), nullable=False)
    university = Column(String(255), nullable=False)