from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from .basic_import import *
from models.subscribers import Subscriber
from models.plans import Plans
from models.products import Products

router = APIRouter()

class SubscriberBase(BaseModel):
    plan_id: int
    product_id: int
    organization_name: str
    contact_name: str
    mobile_number: str
    email: str
    date_of_registration: datetime
    addressline: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    is_active: Optional[bool] = True
 
@router.post("/create-subscriber/")
async def create_subscriber(subscriber_data: SubscriberBase, db: db_dependency):
    plan = db.query(Plans).filter(Plans.plan_id == subscriber_data.plan_id).first()
    if plan is None:
        raise raise_exception(404, "Plan not found")
    product = db.query(Products).filter(Products.product_id == subscriber_data.product_id).first()
    if product is None:
        raise raise_exception(404, "Product not found")

    try:
        subscriber = Subscriber(**subscriber_data.dict())
        db.add(subscriber)
        db.commit()
        db.refresh(subscriber)
        return succes_response(subscriber, "Subscriber created successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.get("/get-subscriber/{subscribers_id}")
async def get_subscriber_by_id(subscribers_id: int, db: db_dependency):
    subscriber = db.query(Subscriber).filter(
        Subscriber.subscribers_id == subscribers_id,
        Subscriber.is_deleted == False
    ).first()
    if subscriber is None:
        raise raise_exception(404, "Subscriber not found")
    return jsonable_encoder(subscriber)

@router.delete("/delete-subscriber/{subscribers_id}")
async def delete_subscriber(subscribers_id: int, db: db_dependency):
    subscriber = db.query(Subscriber).filter(
        Subscriber.subscribers_id == subscribers_id,
        Subscriber.is_deleted == False
    ).first()
    if subscriber is None:
        raise raise_exception(404, "Subscriber not found")
    
    try:
        subscriber.is_deleted = True
        db.commit()
        return succes_response(None, "Subscriber deleted successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.patch("/update-subscriber/{subscribers_id}")
async def update_subscriber(subscribers_id: int, update_data: Dict[str, Optional[str]], db: db_dependency):
    subscriber = db.query(Subscriber).filter(
        Subscriber.subscribers_id == subscribers_id,
        Subscriber.is_deleted == False
    ).first()
    if subscriber is None:
        raise raise_exception(404, "Subscriber not found")
    for key, value in update_data.items():
        if hasattr(subscriber, key) and value is not None:
            setattr(subscriber, key, value)
    try:
        db.commit()
        db.refresh(subscriber)
        return jsonable_encoder(subscriber)
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
