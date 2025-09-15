from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class BioTranslation(Base):
    __tablename__ = "bio_translations"

    id = Column(Integer, primary_key=True, index=True)
    lang_code = Column(String(2), nullable=False)
    bio_code = Column(Text, ForeignKey("bios.bio_code", ondelete="CASCADE"), nullable=False)
    bio_field = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bio = relationship("Bio", back_populates="translations")


