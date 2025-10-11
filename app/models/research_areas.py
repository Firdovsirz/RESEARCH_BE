from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base

class ResearchAreas(Base):
    __tablename__ = 'research_areas'

    id = Column(Integer, primary_key=True, index=True)
    area_code = Column(String, nullable=False, unique=True)
    fin_kod = Column(String(7), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)