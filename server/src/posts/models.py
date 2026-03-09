from sqlalchemy import Column, String, Float, Boolean, DateTime 
from datetime import datetime 
from src.database import Base

class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    idempotency_key = Column(String, unique=True, index=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    sql_validated = Column(Boolean, default=False)
    blockchain_mined = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


