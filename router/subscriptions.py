from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime,timedelta
from .basic_import import *
from models.subscriptions import Subscriptions
from models.plans import Plans
from models.subscribers import Subscriber

router = APIRouter()

class SubscriptionBase(BaseModel):
    plan_id: int
    subscriber_id: int


def create_subscriptions(plan_id, subscriber_id, db):
    plan = db.query(Plans).filter(Plans.plan_id == plan_id).first()
    if plan is None:
        raise raise_exception(404, "Plan not found")
    
    subscriber = db.query(Subscriber).filter(Subscriber.subscribers_id == subscriber_id).first()
    if subscriber is None:
        raise raise_exception(404, "Subscriber not found")
    
    try:
        valid_till = datetime.today().date() + timedelta(days=int(plan.duration_in_days))
        subscription = Subscriptions(
            plan_id=plan_id,
            subscriber_id=subscriber_id,
            date_of_transations=datetime.today(), 
            valid_till=valid_till,
            payment_details="Payment Paid",
            payment_status="Paid",
            remarks="",
            currency="inr",
            amount_paid=plan.amount
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return "Done"
    except Exception as e:
        db.rollback()
        print(e)


@router.post("/create-subscription/")
async def create_subscription(subscription_data: SubscriptionBase, db: db_dependency):
    plan = db.query(Plans).filter(Plans.plan_id == subscription_data.plan_id).first()
    if plan is None:
        raise raise_exception(404, "Plan not found")
    subscriber = db.query(Subscriber).filter(Subscriber.subscribers_id == subscription_data.subscriber_id).first()
    if subscriber is None:
        raise raise_exception(404, "Subscriber not found")
    try:
        subscription = Subscriptions(**subscription_data.dict())
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return succes_response(subscription, "Subscription created successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.get("/get-subscription/{subcrption_id}")
async def get_subscription_by_id(subcrption_id: int, db: db_dependency):
    subscription = db.query(
        Subscriptions,
        Subscriber.organization_name,
        Plans.plan_name
    ).join(
        Subscriber, Subscriptions.subscriber_id == Subscriber.subscribers_id
    ).join(
        Plans, Subscriptions.plan_id == Plans.plan_id
    ).filter(
        Subscriptions.subcrption_id == subcrption_id,
        Subscriptions.is_deleted == False
    ).first()

    if subscription is None:
        raise raise_exception(404, "Subscription not found")
    response = {
        "subcrption_id": subscription.Subscriptions.subcrption_id,
        "plan_id": subscription.Subscriptions.plan_id,
        "plan_name": subscription.plan_name,
        "subscriber_id": subscription.Subscriptions.subscriber_id,
        "organization_name": subscription.organization_name,
        "date_of_transations": subscription.Subscriptions.date_of_transations,
        "valid_till": subscription.Subscriptions.valid_till,
        "payment_details": subscription.Subscriptions.payment_details,
        "payment_status": subscription.Subscriptions.payment_status,
        "remarks": subscription.Subscriptions.remarks,
        "currency": subscription.Subscriptions.currency,
        "amount_paid": subscription.Subscriptions.amount_paid,
        "is_active": subscription.Subscriptions.is_active
    }
    return jsonable_encoder(response)

@router.delete("/delete-subscription/{subcrption_id}")
async def delete_subscription(subcrption_id: int, db: db_dependency):
    subscription = db.query(Subscriptions).filter(
        Subscriptions.subcrption_id == subcrption_id,
        Subscriptions.is_deleted == False
    ).first()
    if subscription is None:
        raise raise_exception(404, "Subscription not found")
    try:
        subscription.is_deleted = True
        db.commit()
        return succes_response(None, "Subscription deleted successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.patch("/update-subscription/{subcrption_id}")
async def update_subscription(subcrption_id: int, update_data: Dict[str, Optional[str]], db: db_dependency,):
    subscription = db.query(Subscriptions).filter(
        Subscriptions.subcrption_id == subcrption_id,
        Subscriptions.is_deleted == False
    ).first()
    if subscription is None:
        raise raise_exception(404, "Subscription not found")
    for key, value in update_data.items():
        if hasattr(subscription, key) and value is not None:
            setattr(subscription, key, value)
    try:
        db.commit()
        db.refresh(subscription)
        return jsonable_encoder(subscription)
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
