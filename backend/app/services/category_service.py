from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.category import Category


def create_category(db : Session, user_id : int, name:str):
    existing = db.query(Category).filter(Category.name == name, Category.user_id == user_id).first()

    if existing:
        raise HTTPException(status_code = 400, detail = "Category already exists")
    
    category = Category(name = name, user_id = user_id)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category

def get_categories(db : Session, user_id : int):

    return db.query(Category).filter(Category.user_id == user_id).all()