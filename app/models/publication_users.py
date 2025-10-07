from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey 
from sqlalchemy.orm import relationship
from app.db.database import Base

class PublicationUsers(Base):
    __tablename__ = 'publication_users'

    id = Column(Integer, primary_key=True, index=True)
    publication_code  = Column(Text, nullable=False)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    image = Column(Text)