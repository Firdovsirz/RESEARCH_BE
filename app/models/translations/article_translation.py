from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base


class ArticleTranslation(Base):
    __tablename__ = "article_translations"

    id = Column(Integer, primary_key=True, index=True)
    lang_code = Column(String(2), nullable=False)
    article_code = Column(Text, ForeignKey("articles.article_code", ondelete='CASCADE'), nullable=False)
    article_field = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    article = relationship("Article", back_populates="translations")