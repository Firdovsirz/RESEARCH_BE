from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base

class ScientificName(Base):
    __tablename__ = 'scientific_names'

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7),ForeignKey("auth.fin_kod"), unique=True, nullable=False)
    scientific_name_code = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)    

    translations = relationship(
        "ScientificNameTranslation", 
        back_populates="scientific_name",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    auth = relationship("Auth", back_populates="scientific_names", passive_deletes=True)