from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(36), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    email = Column(String(100), nullable=False)
    complaint_details = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
