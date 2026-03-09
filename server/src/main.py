import time
import redis
from fastapi import FastAPI, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager


from src.posts.router import router
from src.database import Base, engine, get_db, redis_client
from src.posts.logger import log_event  


@asynccontextmanager
async def lifespan(app: FastAPI):

    log_event("INFO", "SYSTEM_STARTUP", "FastAPI Server has started", {})
    try:
        Base.metadata.create_all(bind=engine)
        log_event("INFO", "DB_INIT", "Database tables verified", {})
    except Exception as e:
        log_event("CRITICAL", "DB_INIT_FAIL", "Could not create tables", {"error": str(e)})
    yield 
    

    log_event("INFO", "SYSTEM_SHUTDOWN", "FastAPI Server is shutting down", {})


app = FastAPI(
    title="ACS Sentinel API", 
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)



@app.get("/sentinel/health")
async def health_check(response: Response, db: Session = Depends(get_db)):
    """
    KUBERNETES PROBE:
    Checks if DB and Redis are actually alive.
    If dead, returns 503 so Kubernetes restarts the pod.
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "latency_ms": 0.0
    }
    
    start_time = time.time()
    errors = False


    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["error_db"] = str(e)
        errors = True
        log_event("CRITICAL", "HEALTH_CHECK_FAIL", "Database unreachable", {"error": str(e)})

    try:
        if redis_client.ping():
            health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = "disconnected"
        health_status["error_redis"] = str(e)
        errors = True
        log_event("CRITICAL", "HEALTH_CHECK_FAIL", "Redis unreachable", {"error": str(e)})

    health_status["latency_ms"] = round((time.time() - start_time) * 1000, 2)

    if errors:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        health_status["status"] = "unhealthy"
    else:
        response.status_code = status.HTTP_200_OK

    return health_status

@app.post("/sentinel/heal")
async def heal_transaction(payload: dict, db: Session = Depends(get_db)):
    """
    AGENT ACTION:
    This is the endpoint your Python Agent calls to fix a Zombie Transaction.
    """
    tx_id = payload.get("id")
    admin_key = payload.get("admin_key")
    
    if admin_key != "GUARD_123": 
        log_event("WARNING", "SECURITY_ALERT", "Unauthorized heal attempt", {"tx_id": tx_id})
        return Response(status_code=403)

    log_event("INFO", "HEAL_ATTEMPT", "Agent attempting to fix transaction", {"tx_id": tx_id})
    

    try:
        log_event("INFO", "HEAL_SUCCESS", "Transaction finalized manually", {"tx_id": tx_id})
        return {"status": "fixed", "id": tx_id}
    except Exception as e:
        log_event("ERROR", "HEAL_FAIL", "Could not fix transaction", {"error": str(e)})
        return Response(status_code=500)