from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class LanguageTranslations(Base):
    __tablename__ = "language_translations"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False)
    lang_code = Column(String(2), nullable=False)
    lang_serial = Column(String)
    language_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)