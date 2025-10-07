from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime
)
from app.db.database import Base

class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint('fin_kod'),
        UniqueConstraint('email'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    fin_kod = Column(String(7), nullable=False, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    birth_date = Column(DateTime, nullable=False)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)