from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    country = Column(String)
    level = Column(String)
    funding = Column(String)
    deadline = Column(String)
    link = Column(String, nullable=False)
    source = Column(String)
    hash = Column(String, unique=True, nullable=False, index=True)
    published_at = Column(DateTime, default=datetime.datetime.utcnow)