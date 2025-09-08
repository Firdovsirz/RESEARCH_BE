from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime
)
from app.db.database import Base

class Otp(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), nullable=False)
    otp = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)