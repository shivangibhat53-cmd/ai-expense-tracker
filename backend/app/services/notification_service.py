from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(db: Session, user_id:int, message : str):
    notification = Notification(user_id = user_id, message = message)

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notifications(db:Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def mark_notification_read(db: Session, user_id: int, notification_id : int):
    notification = db.query(Notification).filter(Notification.user_id == user_id, Notification.id == id).first()

    if notification:
        notification.is_read = True
    
    db.commit()

    return notification
