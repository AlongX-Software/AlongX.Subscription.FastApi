from .basic_import import *
from models.widgets import Dashboard
from models.products import Products
from models.widgets import Widget
from router.login import check_auth_key
router = APIRouter()

Dashboard.metadata.create_all(engine)

class DashboardBase(BaseModel):
    dashboard_name:str  = ""
    product_id:int = 0

@router.post("/create-dashbord/")
async def create_dashboard(dashboard: DashboardBase,db:db_dependency):
    product = await check_instance(Products,"product_id",dashboard.product_id,db)
    if product is None:
        raise raise_exception(404,f"Product not found")
    try:
        dashboard_instnace = Dashboard(**dashboard.dict())
        db.add(dashboard_instnace)
        db.commit()
        db.refresh(dashboard_instnace)
        return succes_response(dashboard_instnace,"Dashboard created successfully")
    except Exception as e:
        # print(e)
        raise raise_exception(500,f"Internal server error {e}")

@router.get("/get-all-dashboard-by-product/")
async def get_all_dashboard_by_product_id(product_id:int,db:db_dependency):
    try:
        dashboards = await get_instances(Dashboard,"product_id",product_id,db)
        return jsonable_encoder(dashboards)
    except Exception as e:
        raise raise_exception(500,f"Internal server error {e}")

@router.get("/get-dashboard-by-id/")
async def get_dashboard_by_id(dashboard_id:int,db:db_dependency):
    dashboard = await check_instance(Dashboard,"dashboard_id",dashboard_id,db)
    if dashboard is None:
        raise raise_exception(404,f"Dashboard not found")
    return jsonable_encoder(dashboard)

@router.patch("/update-dashboard/")
async def update_dashboard(dashboard: DashboardBase,dashboard_id:int,db:db_dependency):
    dashboard_instance = await check_instance(Dashboard,"dashboard_id",dashboard_id,db)
    if dashboard_instance is None:
        raise raise_exception(404,f"Dashboard not found")
    try:
        dashboard_instance.dashboard_name = dashboard.dashboard_name
        db.commit()
        db.refresh(dashboard_instance)
        return succes_response(dashboard_instance,"Dashboard Updated Succesfully")
    except Exception as e:
        raise raise_exception(500,f"Internal server error {e}")

@router.delete("/delete-dashbaord/")
async def delete_dashboard(dashbord_id:int,db:db_dependency):
    dashboard = await check_instance(Dashboard,"dashboard_id",dashbord_id,db)
    if dashboard is None:
        raise raise_exception(404,f"Dashboard not found")
    widget_count = db.query(Widget).filter(Widget.dashboard_id == dashbord_id ).count()
    if widget_count > 0:
        raise raise_exception(400,f"Dashboard has widgets, cannot delete it !")
    try:
        db.delete(dashboard)
        db.commit()
        return succes_response("","Dashboard Deleted")
    except Exception as e:
        raise raise_exception(500,f"Internal server error {e}")



