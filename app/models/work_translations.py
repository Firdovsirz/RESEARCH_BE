from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class WorkTranslations(Base):
    __tablename__ = "work_translations"

    id = Column(Integer, primary_key=True, index=True)
    work_serial = Column(String)
    work_place = Column(String, nullable=False) 
    duty = Column(String)
    language_code = Column(String(2), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)