from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Column,

    Text
)
from app.db.database import Base

class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("users.fin_kod"), nullable=False)
    language_code = Column(String(10), nullable=False)
    language_name = Column(Text, nullable=False)