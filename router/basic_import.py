from database.db import db_dependency,engine
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter,status,WebSocket,WebSocketDisconnect,Depends,BackgroundTasks
from pydantic import BaseModel,Field,EmailStr,validator
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import joinedload
from datetime import datetime
import re,json
from pytz import timezone
from .socket import ConnectionManager
from enum import Enum
from email_send.azure_la import SendNotification
from email_send.currency import get_currency_icon
from .users.login import get_current_user
from whatsapp import Whatsapp
from azure_event_hub import EventHub
import threading
from typing import Optional
from router.receipt import generate_receipt
from models.app_settings import AppSettings
from models.activity_log import ActivityLog

whatsapp = Whatsapp()
notification = SendNotification()

class Role(str, Enum):
    Admin = "Admin"
    User = "User"
    Manager = "Manager"
    Operator = "Operator"


def is_authenticated(*allowed_roles):
    def wrapper(current_user = Depends(get_current_user)):
        target_outlet_id = 0
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        if allowed_roles[0] != "*" and current_user.role.capitalize() not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this action!")

        # if current_user.role.capitalize() not in [Role.Admin]:
        #     if target_outlet_id and current_user.outlet_id != target_outlet_id:
        #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission for this outlet!")
        return current_user
    return wrapper

async def check_instance(model=None,field_name:str=None,field_value=None,db=None):
    try:
        instance = db.query(model).filter(getattr(model, field_name) == field_value,model.is_deleted==False).first()
    except Exception as e:
        instance = db.query(model).filter(getattr(model, field_name) == field_value).first()
    if instance is not None:
        return instance
    return None

async def get_instances(model=None,field_name:str=None,field_value=None,db=None):
    instance = db.query(model).filter(getattr(model, field_name) == field_value,model.is_deleted==False).all()
    if instance is not None:
        return instance
    return None

def raise_exception(error_code:int=None,msg:str=None):
    raise HTTPException(status_code=error_code,detail=jsonable_encoder(msg))

def succes_response(data=None,msg=None):
    return {"status_code":200,"msg":msg,"response":jsonable_encoder(data)}

async def get_current_ist_time():
    ist_timezone = timezone("Asia/Kolkata")
    current_time = datetime.now(ist_timezone)
    return current_time

with open("azure_event_hub/resource.json") as json_file:
    data = json.load(json_file)

async def send_event_notification(event_id:int=0):
    msg = EventHub(data["connectionString"],data["send_event_w"])
    payload = {
        "id":event_id,
    }
    await msg.send_data_to_eventhub(payload)

date_format_mapping = {
    "DD-MM-YYYY": "%d-%m-%Y",
    "MM-DD-YYYY": "%m-%d-%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y",
    "YYYY/MM/DD": "%Y/%m/%d",
    "DD.MM.YYYY": "%d.%m.%Y",
    "MM.DD.YYYY": "%m.%d.%Y",
    "YYYY.MM.DD": "%Y.%m.%d",
    "DD MMM YYYY": "%d %b %Y",
    "MMM DD, YYYY": "%b %d, %Y",
    "YYYY MMM DD": "%Y %b %d",
    "DD Month YYYY": "%d %B %Y",
    "Month DD, YYYY": "%B %d, %Y",
    "YYYY Month DD": "%Y %B %d"
}

def get_time_formate(formate="DD-MM-YYYY"):
    return date_format_mapping.get(formate,"%d-%m-%Y")

class ActivityLogBase(BaseModel):
    org_id: int
    outlet_id: int
    login_id: str
    full_name: str
    operation: str
    operations_con: dict

def create_activtiy_log(activity: ActivityLogBase, db):
    print("I'm being called")
    try:
        activity_log = ActivityLog(**activity.dict())
        activity_log.timestamp = datetime.now()
        db.add(activity_log)
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback() 
        pass