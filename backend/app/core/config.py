from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
from pathlib import Path
import os
from .logging import logger

BASE_DIR = Path(__file__).resolve().parent.parent.parent
logger.info("*************INSIDE CONFIG FILE*************")
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

logger.info("raw: %s", os.getenv("DATABASE_URL"))
loaded = load_dotenv(dotenv_path=env_path)
logger.info("Did dotenv load? %s", loaded)
logger.info("ENV PATH: %s", env_path)

logger.info("Load secrets and keys from env file using loadenv")
#class Settings(BaseModel):
class Settings(BaseSettings):
    DATABASE_URL  : str
    SECRET_KEY  : str
    ALGORITHM  : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REFRESH_TOKEN_EXPIRE_DAYS :int
    RESEND_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
logger.info("DATABASE_URL = %s", settings.DATABASE_URL)


