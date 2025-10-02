from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class InterCoorTranslations(Base):
    __tablename__ = "international_coorperations_translations"

    id = Column(Integer, primary_key=True, index=True)
    language_code = Column(String(2), nullable=False)
    inter_corp_code = Column(String, nullable=False)
    inter_corp_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)