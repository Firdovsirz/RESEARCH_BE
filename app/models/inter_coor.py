from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class InterCoor(Base):
    __tablename__ = "international_coorperations"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False)
    inter_corp_code = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)