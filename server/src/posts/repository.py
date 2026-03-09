from src.posts.logger import log_event
from sqlalchemy.orm import Session
from src.posts.models import Transactions
from src.database import redis_client


class PaymentRepository:


    def __init__(self,db : Session):
        self.db = db 


    def make_payment(self, payment_id: str, key: str, amount: float):
        try:
            record = Transactions(id=payment_id, idempotency_key=key, amount=amount, status="PENDING")
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            log_event("INFO", "DB_COMMIT", "Transaction created successfully", {
                    "tx_id": payment_id, 
                    "amount": amount
                })
            return record
        except Exception as e:
            self.db.rollback()
            log_event("ERROR", "DB_WRITE_FAIL", "Failed to insert transaction", {
                "tx_id": payment_id, 
                "error": str(e)
            })
            raise e


    def get_payment(self,payment_id : str):
        try:
            return self.db.query(Transactions).filter(payment_id == Transactions.id).first()
        except Exception as e:
            log_event("ERROR", "DB_READ_FAIL", "Failed to fetch payment", {
                "tx_id": payment_id, 
                "error": str(e)
            })
            raise e



    def get_all_payment(self,page :int = 1, limits : int = 5):
        try:
            return self.db.query(Transactions).order_by(Transactions.created_at.desc()).offset((page-1)*limits).limit(5).all()
        except Exception as e:
            log_event("ERROR", "DB_READ_FAIL", "Failed to fetch all payments", {
                "page": page, 
                "error": str(e)
            })
            raise e



    def update_status(self,payment_id : str, **updates):
        try:
            self.db.query(Transactions).filter(Transactions.id == payment_id).update(updates)
            self.db.commit()

            log_event("INFO", "DB_UPDATE", "Transaction status updated", {
                "tx_id": payment_id, 
                "updates": updates
            })
        except Exception as e:
            self.db.rollback()
            log_event("ERROR", "DB_UPDATE_FAIL", "Failed to update status", {
                "tx_id": payment_id, 
                "updates": updates, 
                "error": str(e)
            })
            raise e



    def get_cached_id(self,key:str):
        try:
            val = redis_client.get(key)
            if val:
                log_event("WARNING", "IDEMPOTENCY_HIT", "Duplicate request detected", {"key": key})
            else:
                log_event("INFO", "IDEMPOTENCY_MISS", "New unique request", {"key": key})
            return val
        
        except Exception as e:
            log_event("CRITICAL", "REDIS_DOWN", "Cannot connect to Redis", {})
            return None
        except Exception as e:
            log_event("ERROR", "REDIS_ERROR", "Unexpected Redis error", {"error": str(e)})
            return None



    def set_cached_id(self,key:str,payment_id:str):
        try:
            redis_client.setex(key, 86400, payment_id)
        except Exception as e:
            log_event("CRITICAL", "REDIS_DOWN", "Cannot write to Redis", {})
        except Exception as e:
            log_event("ERROR", "REDIS_WRITE_FAIL", "Failed to cache key", {"error": str(e)})





