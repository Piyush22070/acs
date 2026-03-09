import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session


from src.posts.constants import TRANSACTION_TAG
from src.posts.schemas import TransactionCreate, PaymentStatus
from src.database import get_db
from src.posts.repository import PaymentRepository
from src.posts.service import PaymentService



router = APIRouter(prefix="/payments",tags=TRANSACTION_TAG)



@router.post("")
async def create_transaction(data: TransactionCreate,bg: BackgroundTasks,db= Depends(get_db)):

    try:
        repo = PaymentRepository(db)
        svc = PaymentService()

        
        try:
            cached_id = repo.get_cached_id(data.idempotencyKey)

            if cached_id:
                payment = repo.get_payment(cached_id)
                if payment:
                    return payment
                
        except Exception as e:

            raise HTTPException(status_code=500, detail=str(e))
        
        new_id = f"pay_{uuid.uuid4().hex[:6]}"

        record = repo.make_payment(new_id, data.idempotencyKey , data.amount)

        repo.set_cached_id(data.idempotencyKey, new_id)

        bg.add_task(svc.run_full_lifecycle, new_id)

        return record
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("", response_model=list[PaymentStatus])
async def list_transactions(page:int=1, db: Session = Depends(get_db)):
    return PaymentRepository(db).get_all_payment(page)



@router.get("/{id}",response_model=PaymentStatus)
async def get_payment(id: str, db: Session = Depends(get_db)):
    payement = PaymentRepository(db).get_payment(id)
    if not payement:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payement



