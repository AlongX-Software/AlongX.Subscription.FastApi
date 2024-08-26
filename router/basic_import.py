from database.db import db_dependency,engine
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter,status,WebSocket,WebSocketDisconnect,Depends,BackgroundTasks
from pydantic import BaseModel,Field,EmailStr,validator
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import joinedload
from datetime import datetime
import re,json
from pytz import timezone
from enum import Enum
import threading
from typing import Optional

class Role(str, Enum):
    Admin = "Admin"
    User = "User"

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
