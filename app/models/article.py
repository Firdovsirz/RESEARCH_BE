from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7),ForeignKey("auth.fin_kod"), nullable=False)
    article_code = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)    

    translations = relationship(
        "ArticleTranslation", 
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    auth = relationship("Auth", back_populates="articles", passive_deletes=True)







