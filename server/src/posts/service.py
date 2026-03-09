import time
from src.posts.logger import log_event
from src.database import SessionLocal
from src.posts.repository import PaymentRepository

class PaymentService:
    def run_full_lifecycle(self, payment_id: str):
        """Simulates the backend processing lifecycle."""
        with SessionLocal() as db:
            repo = PaymentRepository(db)
            try:
                
                time.sleep(4)
                repo.update_status(payment_id, status="validated", sql_validated=True)
                log_event("INFO", "PAYMENT_VALIDATED", f"Payment {payment_id} validated in SQL", {"payment_id": payment_id})
                
              
                time.sleep(8)
                repo.update_status(payment_id, status="finalized", blockchain_mined=True)
                log_event("INFO", "PAYMENT_FINALIZED", f"Payment {payment_id} mined on blockchain", {"payment_id": payment_id})


            except Exception as e:
                db.rollback()
                log_event("ERROR", "PAYMENT_PROCESSING_FAIL", f"Failed to process payment {payment_id}", {"payment_id": payment_id, "error": str(e)})