import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Load environment variables securely
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Establish the database engine connection pool
engine = create_engine(DATABASE_URL)

# 3. Create a factory for individual database sessions
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 4. Modern SQLAlchemy 2.0 Base Class (Replaces declarative_base)
class Base(DeclarativeBase):
    pass