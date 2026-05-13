from fastapi import FastAPI
from app.db.database import Base, engine
from app.models.user import User

Base.metadata.create_all(bind = engine)
app = FastAPI()

@app.get("/")
def home():
    return {"message":"AI Finance Platform API"}