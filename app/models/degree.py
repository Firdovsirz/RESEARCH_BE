from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Column,
    Text
)
from app.db.database import Base

class ScientificDegree(Base):
    __tablename__ = "scientific_degrees"

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("users.fin_kod"), nullable=False)
    scientific_degree_code = Column(String(10), nullable=False)
    scientific_degree_name = Column(Text, nullable=False)