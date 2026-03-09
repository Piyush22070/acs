import os
import redis
from src.posts.logger import log_event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/acs_db")

engine = create_engine(
    DATABASE_URL, 
    pool_size=10, 
    max_overflow=20, 
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

try:
    redis_client.ping()
except redis.ConnectionError:
    log_event("CRITICAL", "REDIS_CONNECTION_FAIL", "Could not connect to Redis", {})

def get_db():
    db = SessionLocal()
    try:
        yield db 
    except Exception as e:
        log_event("CRITICAL", "DB_CONNECTION_FAIL", "Could not connect to Postgres", {"error": str(e)})
    finally:
        db.close()