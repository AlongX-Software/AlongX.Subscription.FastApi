from .basic_import import *

class Subscriptions(BASE):
    __tablename__ = "tbl_subscriptions"
    subcrption_id  = Column(BigInteger, primary_key=True, autoincrement=True)
    plan_id = Column(BigInteger,ForeignKey("tbl_plans.plan_id",ondelete="SET NULL"))
    subscriber_id = Column(BigInteger,ForeignKey("tbl_subscribers.subscribers_id",ondelete="SET NULL"))
    date_of_transations= Column(DateTime)
    valid_till = Column(DateTime)
    payment_details = Column(Text)   
    payment_status = Column(Text)  
    remarks = Column(Text)  
    currency =  Column(Text)
    amount_paid = Column (Float)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)