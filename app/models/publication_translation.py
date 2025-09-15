from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base


class PublicationTranslation(Base):
    __tablename__ = "publication_translations"

    id = Column(Integer, primary_key=True, index=True)
    lang_code = Column(String(2), nullable=False)
    publication_code = Column(Text, ForeignKey("publications.publication_code", ondelete='CASCADE'), nullable=False)
    publication_name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    publication = relationship("Publication", back_populates="translations")



