from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Bio(Base):
    __tablename__ = 'bios'

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("auth.fin_kod"), unique=True, nullable=False) 
    bio_code = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    translations = relationship(
        "BioTranslation", 
        back_populates="bio", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    auth = relationship("Auth", back_populates="bios",passive_deletes=True)

















