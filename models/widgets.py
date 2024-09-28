from .basic_import import *

class Widget(BASE):
    __tablename__ = "tbl_widget"
    widget_id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    dashboard_id = Column(Integer)
    widget_name = Column(Text,nullable=True)
    widget_type = Column(Text,nullable=True)
    widget_query = Column(Text,nullable=True)
    position = Column(Integer,default=1,nullable=True)
    height =  Column(Integer,default=6,nullable=True)
    width = Column(Integer,default=6,nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

class Dashboard(BASE):
    __tablename__ = "tbl_dashboard"
    dashboard_id = Column(Integer, primary_key=True)
    dashboard_name = Column(String(255),nullable=False)
    product_id = Column(BigInteger,ForeignKey("tbl_products.product_id",ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

