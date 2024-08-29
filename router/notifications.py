from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from .basic_import import *
from models.notifications import Notification
from router.login import check_auth_key
router = APIRouter()

class NotificationCreate(BaseModel):
    product_id: int
    subscriber_id: int
    plan_name: str
    notification_title: str
    description: str

@router.post("/create-notification/")
async def create_notification(notification_data: NotificationCreate, db: db_dependency):
    try:
        notification = Notification(**notification_data.dict())
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return succes_response(notification, "Notification created successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.get("/get-notifications/")
async def get_notifications(product_id: int,  subscriber_id: Optional[int] , db: db_dependency,user_id: int = Depends(check_auth_key)):
    try:
        query = db.query(Notification).filter(Notification.product_id == product_id, Notification.is_deleted == False)
        if subscriber_id:
            query = query.filter(Notification.subscriber_id == subscriber_id)
        notifications = query.all()

        if not notifications:
            raise raise_exception(404, "No notifications found")

        return jsonable_encoder(notifications)
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.delete("/delete-notification/{notification_id}")
async def delete_notification(notification_id: int, db: db_dependency,user_id: int = Depends(check_auth_key)):
    try:
        notification = await check_instance(Notification, "notifications_id", notification_id, db)
        if notification is None:
            raise raise_exception(404, "Notification not found")

        notification.is_deleted = True
        db.commit()
        return succes_response(notification, "Notification deleted successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
