from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user
from typing import List

from app.models.user import User

from app.schemas.notification import (NotificationResponse)
import app.services.notification_service as service

router = APIRouter(prefix = "/notifications", tags = ["Notifications"])

@router.get("/",response_model = List[NotificationResponse])
def get_all_notifications(db: Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return service.get_notifications(db, current_user.id)


@router.put("/{notification_id}/read")
def mark_read(notification_id: int,db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    return service.mark_notification_read(db,current_user.id, notification_id)