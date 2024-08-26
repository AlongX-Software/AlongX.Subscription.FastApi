from .basic_import import *

class Subscriber(BASE):
    __tablename__ = "tbl_subscribers"
    subscribers_id  = Column(BigInteger, primary_key=True, autoincrement=True)
    plan_id = Column(BigInteger,ForeignKey("tbl_plans.plan_id",ondelete="SET NULL"))
    product_id = Column(BigInteger,ForeignKey("tbl_products.product_id",ondelete="SET NULL"))
    organization_name = Column(Text)   
    contact_name = Column(Text)  
    mobile_number = Column(Text)  
    email =  Column(Text)
    date_of_registration = Column(DateTime)
    addressline = Column(Text)
    city = Column(Text)
    state = Column(Text)
    country = Column(Text)
    pincode = Column(Text)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)