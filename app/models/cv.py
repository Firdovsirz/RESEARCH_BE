from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime
)
from app.db.database import Base

class Cv(Base):
    __tablename__ = "cv"
    __table_args__ = (
        UniqueConstraint("fin_kod"),
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False, unique=True)
    cv_path = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)