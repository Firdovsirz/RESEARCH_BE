from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base

class ResearchAreasTranslations(Base):
    __tablename__ = 'research_areas_translations'

    id = Column(Integer, primary_key=True, index=True)
    area_code = Column(String, nullable=False, unique=True)
    lang_code = Column(String(2), nullable=False)
    area = Column(String, nullable=False)