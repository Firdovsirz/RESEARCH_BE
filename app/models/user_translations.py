from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    CheckConstraint,
    ForeignKey,
    DateTime
)
from app.db.database import Base

class UserTranslations(Base):
    __tablename__ = "user_translations"
    __table_args__ = (
        UniqueConstraint('fin_kod'),
        CheckConstraint("lang_code_check IN ('en', 'az')", name="lang_code")
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("user.fin_kod"), nullable=False, unique=True)
    lang_code = Column(String(2), nullable=False)
    work_place = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)