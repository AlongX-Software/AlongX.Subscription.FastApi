from fastapi import APIRouter, HTTPException
from sqlalchemy import desc
from datetime import datetime
from models.subscribers import Subscriber
from models.plans import Plans
from .basic_import import *
from models.subscriptions import Subscriptions
from pydantic import BaseModel

router = APIRouter()

class AccountValidation(BaseModel):
    status: bool
    OrganizationName: str
    PlanId: int
    PlanName: str
    LastDateOfTransaction: datetime
    ValidTill: datetime
    RemainingDays: int
    Message: str

@router.get("/validate-account/{subscriber_id}", response_model=AccountValidation)
async def validate_account(subscriber_id: int, db: db_dependency):
    latest_subscription = db.query(Subscriptions).filter(
        Subscriptions.subscriber_id == subscriber_id,
        Subscriptions.is_deleted == False
    ).order_by(desc(Subscriptions.date_of_transations)).first()  
    if not latest_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    plan = db.query(Plans).filter(Plans.plan_id == latest_subscription.plan_id, Plans.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    valid_till_date = latest_subscription.valid_till
    today = datetime.utcnow()
    remaining_days = (valid_till_date - today).days
    response = AccountValidation(
        status=remaining_days >= 0,
        OrganizationName=None if not latest_subscription else (db.query(Subscriber).filter(Subscriber.subscribers_id == subscriber_id).first().organization_name),
        PlanId=latest_subscription.plan_id,
        PlanName=plan.plan_name,
        LastDateOfTransaction=latest_subscription.date_of_transations,
        ValidTill=valid_till_date,
        RemainingDays=remaining_days,
        Message="Your Subscription is Active" if remaining_days >= 0 else f"Your Subscription has been Expired {-remaining_days} Days back"
    )
    return response
