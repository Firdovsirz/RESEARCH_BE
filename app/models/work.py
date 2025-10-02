from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class Work(Base):
    __tablename__ = "work"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False)
    work_serial = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)