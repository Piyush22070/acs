from pydantic import BaseModel
from datetime import datetime

class TransactionCreate(BaseModel):
    amount : float
    idempotencyKey: str


class PaymentStatus(BaseModel):
    id: str
    amount: float
    status: str
    sql_validated: bool
    blockchain_mined: bool
    created_at: datetime 
