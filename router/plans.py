from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .basic_import import *
from models.plans import Plans
from models.products import Products

router = APIRouter()

class PlanBase(BaseModel):
    plan_name: str
    product_id: int
    duration_in_days: str
    Currency: str
    amount: float
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)

@router.post("/create-plan/")
async def create_plan(plan_data: PlanBase, db: db_dependency):
    product = db.query(Products).filter(Products.product_id == plan_data.product_id).first()
    if product is None:
        raise raise_exception(404, "Product not found") 
    try:
        plan = Plans(**plan_data.dict())
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return succes_response(plan, "Plan created successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.get("/get-plans-by-product/{product_id}")
async def get_plans_by_product(product_id: int, db: db_dependency):
    plans = db.query(Plans).filter(
        Plans.product_id == product_id,
        Plans.is_deleted == False
    ).all()
    return jsonable_encoder(plans)

@router.delete("/delete-plan/{plan_id}")
async def delete_plan(plan_id: int, db: db_dependency):
    plan = db.query(Plans).filter(
        Plans.plan_id == plan_id,
        Plans.is_deleted == False
    ).first()
    if plan is None:
        raise raise_exception(404, "Plan not found")
    try:
        plan.is_deleted = True
        db.commit()
        return succes_response(None, "Plan deleted successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")
