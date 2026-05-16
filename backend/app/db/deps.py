from app.db.session import get_session_local
from app.core.logging import logger
def get_db():
    logger.info("*********INSIDE DEPS**********")
    SessionLocal = get_session_local()
    db = SessionLocal()

    logger.info("Called db--> Session Local")
    try:
        yield db
    finally:
        db.close()