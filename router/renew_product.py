from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from .basic_import import *
from models.subscribers import Subscriber
from models.plans import Plans
from models.subscriptions import Subscriptions

router = APIRouter()

class RenewProduct(BaseModel):
    subscriber_id: int
    plan_id: int
    payment_details: str
    payment_status: str
    remarks: str
    amount_paid: float
    currency: str
    is_active: bool

@router.post("/renew-product/")
async def renew_product(request: RenewProduct, db: db_dependency):
    try:
        plan = db.query(Plans).filter(Plans.plan_id == request.plan_id, Plans.is_deleted == False).first()
        if plan is None:
            raise raise_exception(404, "Plan not found")
        subscriber = db.query(Subscriber).filter(Subscriber.subscribers_id == request.subscriber_id, Subscriber.is_deleted == False).first()
        if subscriber is None:
            raise raise_exception(404, "Subscriber not found")
        duration_in_days = int(plan.duration_in_days)
        valid_till_date = datetime.utcnow() + timedelta(days=duration_in_days)
        new_subscription = Subscriptions(
            plan_id=request.plan_id,
            subscriber_id=request.subscriber_id,
            date_of_transations=datetime.utcnow(),
            valid_till=valid_till_date,
            payment_details=request.payment_details,
            payment_status=request.payment_status,
            remarks=request.remarks,
            amount_paid=request.amount_paid,
            currency=request.currency,
            is_active=request.is_active,
            is_deleted=False
        )
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)  
        return succes_response(new_subscription, "Product subscription renewed successfully")
    except Exception as e:
        raise raise_exception(500, f"Operation failed: {e}")
