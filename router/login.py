from typing import Optional
from database.db import db_dependency
from fastapi import Depends, Request, HTTPException, status, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from models.valid_keys import AuthKeys

router = APIRouter()

@router.post("/login")
async def login_with_auth_key(
    request: Request,
    db: db_dependency
):
    # Retrieve the X-Auth-Key from headers
    key = request.headers.get("X-Auth-Key")
    if not key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auth key is required")

    # Validate the key against the database
    valid_key = db.query(AuthKeys).filter(
        AuthKeys.key_value == key,
        AuthKeys.is_active == True,
        AuthKeys.expiry_date > datetime.utcnow()
    ).first()

    if not valid_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired key")
    return "Login"

def check_auth_key(request: Request, db:db_dependency):
    key = request.headers.get("X-Auth-Key")
    if not key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auth key is required")
    valid_key = db.query(AuthKeys).filter(
        AuthKeys.key_value == key,
        AuthKeys.is_active == True
    ).first()

    if not valid_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired key")
    return valid_key.subscriber_id


@router.get("/protected-data/")
async def get_protected_data(request: Request, db:db_dependency):
    user_id = check_auth_key(request, db)
    return {
        "message": "This is protected data",
        "user_id": user_id
    }