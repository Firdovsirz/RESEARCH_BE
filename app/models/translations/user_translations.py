from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from app.db.database import Base

class UserTranslations(Base):
    __tablename__ = "user_translations"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False)
    language_code = Column(String(2), nullable=False)
    scientific_degree_name = Column(String, nullable=False)
    scientific_name = Column(String, nullable=False)
    bio = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)