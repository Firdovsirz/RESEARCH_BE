from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    edu_code = Column(String(7),unique=True, nullable=False)
    start_date = Column(Integer, nullable=False)
    end_date = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)