from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class Auth(Base):
    __tablename__ = "auth"
    __table_args__ = (
        UniqueConstraint('fin_kod'),
        UniqueConstraint('email'),
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    role = Column(Integer, nullable=False, default=2)
    password = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)


    articles = relationship(
        "Article",
        back_populates="auth",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    bios = relationship(
        "Bio",
        back_populates="auth",
        cascade="all, delete-orphan"
    )

    scientific_names = relationship(
        "ScientificName",
        back_populates="auth",
        cascade="all, delete-orphan"
    )