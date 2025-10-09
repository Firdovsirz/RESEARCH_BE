from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False)
    exp_code = Column(String(7), unique=True, nullable=False)
    start_date = Column(Integer, nullable=False)
    end_date = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)