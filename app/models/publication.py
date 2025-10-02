from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base

class Publication(Base):
    __tablename__ = 'publications'

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7),ForeignKey("auth.fin_kod"), nullable=False)
    publication_code = Column(Text, unique=True, nullable=False)
    publication_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)    

    translations = relationship(
        "PublicationTranslation", 
        back_populates="publication",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    auth = relationship("Auth", back_populates="publications", passive_deletes=True) 

    from app.models.translations.publication_translation import PublicationTranslation