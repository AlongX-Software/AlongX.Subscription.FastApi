from sqlalchemy import desc
from datetime import datetime
from enum import Enum
from router.basic_import import *
from router.login import check_auth_key
from models.widgets import Widget
from models.products import Products
from .chat_query import WidgetProcessor
import time
Widget.metadata.create_all(engine)
router = APIRouter()

class ChartType(str,Enum):
    Line = "Line"
    Bar = "Bar"
    Pie = "Pie"
    Scatter = "Scatter"
    Radar = "Radar"
    Area = "Area"
    Bubble = "Bubble"
    Heatmap = "Heatmap"
    Gauge = "Gauge"
    Table = "Table"
    Card = "Card"


class WidgetBase(BaseModel):
    product_id:int = 0
    dashboard_id:int = 0
    widget_name:str = ""
    widget_type:ChartType = ChartType.Line
    widget_query:str = ""
    position: int
    height:int = 0
    width:int = 0

@router.get("/get-all-widgets-by-product-dashboard-vise/")
async def get_all_widgets_by_product_id(product_id: int,dashboard_id:int,db: db_dependency):
    try:
        widgets = db.query(Widget).filter(Widget.is_deleted == False, Widget.product_id == product_id,Widget.dashboard_id == dashboard_id).order_by(Widget.position.asc()).all()        
        widget_processor = WidgetProcessor(widgets)
        processed_data = widget_processor.process_data()
        return processed_data
    except Exception as e:
        raise raise_exception(500, f"Internal server error: {e}")

@router.post("/create-new-widget/")
async def create_new_widget(widget: WidgetBase, db: db_dependency):
    product = await check_instance(Products,"product_id",widget.product_id,db)
    if not product:
        raise raise_exception(404,f"Product not found")
    try:
        widget_instance = Widget(**widget.dict())
        db.add(widget_instance)
        db.commit()
        return succes_response("","Widget created successfully")
    except Exception as e:
        db.rollback()
        return raise_exception(500,f"Internal server error {e}")

@router.delete("/delete-widget/")
async def remove_widget(widget_id:int,db:db_dependency):
    widget = await check_instance(Widget,"widget_id",widget_id,db)
    if widget is None:
        raise raise_exception(404,f"Widget not found")
    try:
        db.delete(widget)
        db.commit()
        return succes_response("","Widget deleted successfully")
    except Exception as e:
        db.rollback()
        return raise_exception(500,f"Internal server error {e}")

@router.get("/get-wiget-data/")
async def get_widget_data(widget_id: int, db: db_dependency):
    widget = await check_instance(Widget,"widget_id",widget_id,db)
    if widget is None:
        raise raise_exception(404,f"Widget not found")
    return jsonable_encoder(widget)

@router.patch("/update-widget/")
async def update_widget(widget_id: int, widget: WidgetBase, db: db_dependency):
    widget_instance = await check_instance(Widget,"widget_id",widget_id,db)
    if widget_instance is None:
        raise raise_exception(404,f"Widget not found")
    try:
        for key,val in widget.__dict__.items():
            if key != "product_id" and val:
                setattr(widget_instance,key,val)
        db.commit()
        db.refresh(widget_instance)
        return succes_response(widget_instance, "Widget updated successfully")
    except Exception as e:
        print(e)
        raise raise_exception(500, f"Operation failed: {e}")
    
class UpdateWidgetPositionRequest(BaseModel):
    widget_id: int
    position: int

@router.patch("/update-widget-position/")
async def update_widget_position(request: UpdateWidgetPositionRequest, db:db_dependency):
    widget_instance = await check_instance(Widget, "widget_id", request.widget_id, db)
    if widget_instance is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    widget_instance.position = request.position
    db.add(widget_instance)
    db.commit()
    db.refresh(widget_instance)
    return succes_response("","Widget position updated successfully")
