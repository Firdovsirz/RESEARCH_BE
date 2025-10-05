from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Column,

    Text
)
from app.db.database import Base

class Links(Base):
    __tablename__ = "links"
    
    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False, unique=True)
    scopus_url = Column(Text, nullable=True)
    webofscience_url = Column(Text, nullable=True)
    google_scholar_url = Column(Text, nullable=True)
