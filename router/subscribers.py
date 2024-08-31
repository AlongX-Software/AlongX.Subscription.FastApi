from typing import Optional, Dict
from datetime import datetime,timedelta
from .basic_import import *
from models.subscribers import Subscriber
from models.valid_keys import AuthKeys
from models.plans import Plans
from models.products import Products
from models.subscriptions import Subscriptions
import random
from router.login import check_auth_key
AuthKeys.metadata.create_all(engine)

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

class SubscriberUpdate(BaseModel):
    plan_id: Optional[int] = None
    product_id: Optional[int] = None
    organization_name: Optional[str] = None
    contact_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    addressline: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    is_active: Optional[bool] = None

def genare_auth_key(limit=16):
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIFJKMLNO') for _ in range(limit))

async def is_auth_key_unique(db):
    auth_key = genare_auth_key()
    while db.query(AuthKeys).filter(AuthKeys.key_value == auth_key).first():
        auth_key = genare_auth_key()
    return auth_key

async def create_auth_key(db,sub_id: int,plan_days:str):
    auth_key = await is_auth_key_unique(db)
    try:
        auth = AuthKeys(
            key_value=auth_key,
            subscriber_id=sub_id,
        )
        auth.key_valid_till = datetime.now() + timedelta(days=int(plan_days))
        db.add(auth)
        db.commit()
        return auth_key
    except Exception as e:
        print(f"Error creating auth key: {e}")
        db.rollback()

# @router.get("/finish-prev-subs/")
# async def finish_prev_subs(db:db_dependency):
#     all_subs = db.query(Subscriber).all()
#     for sub in all_subs:
#         sub_current_subscription = db.query(Subscriptions)\
#                 .filter(Subscriptions.subscriber_id == sub.subscribers_id)\
#                 .order_by(Subscriptions.subcrption_id.desc())\
#                 .first()
#         if sub_current_subscription:
#             auth_key = await is_auth_key_unique(db)
#             try:
#                 auth = AuthKeys(
#                     key_value=auth_key,
#                     subscriber_id=sub.subscribers_id,
#                     key_valid_till=sub_current_subscription.valid_till 
#                 )
#                 db.add(auth)
#                 db.commit()
#                 print(f"Auth key generated for subscriber ID {sub.subscribers_id}")
#             except Exception as e:
#                 print(f"Error creating auth key for subscriber ID {sub.subscribers_id}: {e}")
#                 db.rollback()

@router.post("/create-subscriber/")
async def create_subscriber(subscriber_data: SubscriberBase, db: db_dependency, background: BackgroundTasks):
    plan = db.query(Plans).filter(Plans.plan_id == subscriber_data.plan_id).first()
    if plan is None:
        raise raise_exception(404, "Plan not found")
    
    product = db.query(Products).filter(Products.product_id == subscriber_data.product_id).first()
    if product is None:
        raise raise_exception(404, "Product not found")
    
    existing_email = db.query(Subscriber).filter(
        Subscriber.product_id == subscriber_data.product_id,
        Subscriber.email == subscriber_data.email,
        Subscriber.is_active == True
    ).first()
    if existing_email:
        raise raise_exception(409, f"Email already exists for this product")
    
    existing_mobile = db.query(Subscriber).filter(
        Subscriber.product_id == subscriber_data.product_id,
        Subscriber.mobile_number == subscriber_data.mobile_number,
        Subscriber.is_active == True
    ).first()
    if existing_mobile:
        raise raise_exception(409, f"Mobile number already exists for this product")
    
    try:
        subscriber = Subscriber(**subscriber_data.dict())
        db.add(subscriber)
        db.commit()
        db.refresh(subscriber)
        auth_key = await create_auth_key(db, subscriber.subscribers_id,plan.duration_in_days)
        payload = {
            "subscribers_id":subscriber.subscribers_id,
            "auth_key":auth_key
        }
        background.add_task(create_subscriptions, plan.plan_id, subscriber.subscribers_id, db)
        return succes_response(payload,"Subscriber created successfully")
    except Exception as e:
        db.rollback()
        raise raise_exception(500, f"Internal Server Error: {e}")

async def create_subscriptions(plan_id: int, subscriber_id: int, db):
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
            date_of_transations=datetime.now(),  # Corrected attribute name
            valid_till=valid_till.strftime("%Y-%m-%d 23:59:59"),
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


@router.get("/get-subscriber/{subscribers_id}")
async def get_subscriber_by_id(subscribers_id: int, db: db_dependency,user_id: int = Depends(check_auth_key)):
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
async def update_subscriber(subscribers_id: int, update_data: SubscriberUpdate, db: db_dependency,user_id: int = Depends(check_auth_key)):
    subscriber = db.query(Subscriber).filter(
        Subscriber.subscribers_id == subscribers_id,
        Subscriber.is_deleted == False
    ).first()   
    if subscriber is None:
        raise raise_exception(404, "Subscriber not found")
    update_data = update_data.dict(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(subscriber, key, value)
    try:
        db.commit()
        db.refresh(subscriber)
        return jsonable_encoder(subscriber)
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
