from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Column,

    Text
)
from app.db.database import Base

class Scopus(Base):
    __tablename__ = "scopus"
    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("user.fin_kod"), nullable=False, unique=True)
    scopus_url = Column(Text, nullable=False)