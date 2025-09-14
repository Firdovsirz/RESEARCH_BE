from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Column,
    Table,
    Text
)
from app.db.database import Base
from sqlalchemy.orm import relationship

#many to many relation
user_languages_table = Table(
    "user_languages",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("language_code", String, primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    languages = relationship("Language", secondary=user_languages_table, back_populates="users")

class Language(Base):
    __tablename__ = "languages"

    code = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    users = relationship("User", secondary=user_languages_table, back_populates="languages")
