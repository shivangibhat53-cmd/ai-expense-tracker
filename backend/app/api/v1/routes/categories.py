from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.deps import get_db
from app.api.deps import get_current_user

from app.models.user import User

from app.schemas.category import (CategoryCreate, CategoryResponse)
import app.services.category_service as service


router = APIRouter(prefix = "/categories", tags = ["Categories"])

@router.post("/", response_model = CategoryResponse)
def create_category(data : CategoryCreate, db: Session = Depends(get_db), current_user : User = Depends(get_current_user)):
        return service.create_category(
        db,
        current_user.id,
        data.name
    )


@router.get("/", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_categories(
        db,
        current_user.id
    )