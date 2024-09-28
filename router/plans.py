from .basic_import import *
from models.plans import Plans
from models.subscribers import Subscriber
from models.products import Products
from router.login import check_auth_key
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
async def get_plans_by_product(product_id: int, db:db_dependency):
    plans = db.query(Plans).filter(
        Plans.product_id == product_id,
        Plans.is_deleted == False
    ).all()
    return jsonable_encoder(plans)

@router.get("/get-plan-by-id/")
async def get_plans_by_product(plan_id: int, db:db_dependency):
    plan = await check_instance(Plans, "plan_id", plan_id, db)
    if plan is None:
        raise raise_exception(404, "Plan not found")       
    return jsonable_encoder(plan)


@router.delete("/delete-plan/{plan_id}")
async def delete_plan(plan_id: int,db: db_dependency,user_id: int = Depends(check_auth_key)):
    try:
        subscriber_exists = db.query(Subscriber).filter(Subscriber.plan_id == plan_id, Subscriber.is_deleted == False).first()
        if not subscriber_exists:
            plan = await check_instance(Plans, "plan_id", plan_id, db)
            if plan is None:
                raise raise_exception(404, "Plan not found")       
            plan.is_deleted = True
            db.commit()
            return succes_response(plan, "Plan deleted successfully")
        else:
            raise raise_exception(400, "Cannot delete plan as it is being used by a Subscriber")
    except Exception as e:
        raise raise_exception(500, f"Operation failed: {e}")
    

@router.patch("/update-plan/")
async def update_plan(plan_id:int,plan:PlanBase,db:db_dependency,user_id: int = Depends(check_auth_key)):
    plan_exists = await check_instance(Plans, "plan_id", plan_id, db)
    if plan_exists is None:
        raise raise_exception(404, "Plan not found")
    try:
        for key,val in plan.__dict__.items():
            if key != "product_id":
                setattr(plan_exists,key,val)
        db.commit()
        db.refresh(plan_exists)
        return succes_response(plan_exists, "Plan updated successfully")
    except Exception as e:
        print(e)
        raise raise_exception(500, f"Operation failed: {e}")
