from .basic_import import *

class Plans(BASE):
    __tablename__="tbl_plans"
    plan_id = Column(BigInteger,primary_key=True,autoincrement=True)
    plan_name = Column(Text)
    product_id = Column(BigInteger,ForeignKey("tbl_products.product_id",ondelete="SET NULL"))
    duration_in_days = Column(Text)
    Currency = Column(Text)
    amount = Column (Float)
    is_active = Column(Boolean,default=True)
    is_deleted = Column(Boolean,default=False)
