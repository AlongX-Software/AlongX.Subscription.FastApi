from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from .basic_import import *
from models.subscriptions import Subscriptions
from models.plans import Plans
from models.subscribers import Subscriber
from router.login import check_auth_key

router = APIRouter()

@router.get("/get-subscriptions-by-subscriber/{subscriber_id}")
async def get_subscriptions_by_subscriber(subscriber_id: int, db: db_dependency,user_id: int = Depends(check_auth_key)):
    subscriptions = db.query(
        Subscriptions,
        Subscriber.organization_name,
        Plans.plan_name,
        Plans.product_id
    ).join(
        Subscriber, Subscriptions.subscriber_id == Subscriber.subscribers_id
    ).join(
        Plans, Subscriptions.plan_id == Plans.plan_id
    ).filter(
        Subscriptions.subscriber_id == subscriber_id,
        Subscriptions.is_deleted == False
    ).all()

    if not subscriptions:
        raise raise_exception(404, "No subscriptions found for the given subscriber")
    response = []
    for subscription in subscriptions:
        response.append({
            "subcrption_id": subscription.Subscriptions.subcrption_id,
            "plan_id": subscription.Subscriptions.plan_id,
            "plan_name": subscription.plan_name,
            "product_id": subscription.product_id,
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
        })
    return jsonable_encoder(response)
