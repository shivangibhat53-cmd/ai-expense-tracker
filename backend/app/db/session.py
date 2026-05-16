from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logging import logger

logger.info("Creating database engine")
#engine = create_engine(settings.DATABASE_URL)
def get_engine():
    logger.info("Inside get_enginer")
    return create_engine(settings.DATABASE_URL, pool_pre_ping = True)


def get_session_local():
    logger.info("Inside function get_session_local")
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=get_engine()
    )
logger.info("******CREATED SESSION***********")
