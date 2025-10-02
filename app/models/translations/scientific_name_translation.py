from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base


# scientific_name_translation.py
class ScientificNameTranslation(Base):
    __tablename__ = "scientific_name_translations"

    id = Column(Integer, primary_key=True, index=True)
    lang_code = Column(String(2), nullable=False)
    scientific_name_code = Column(Integer, ForeignKey("scientific_names.scientific_name_code", ondelete='CASCADE'), nullable=False)
    scientific_name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # add relationship back to ScientificName
    scientific_name = relationship("ScientificName", back_populates="translations")