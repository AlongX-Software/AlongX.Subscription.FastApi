from .basic_import import *
from datetime import datetime

class Notification(BASE):
    __tablename__ = 'tbl_notifications'
    notifications_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger,ForeignKey("tbl_products.product_id",ondelete="SET NULL"))
    subscriber_id = Column(BigInteger)
    plan_name = Column(String(255))
    date = Column(Date,default=datetime.utcnow)
    notification_title = Column(Text) 
    description = Column(Text) 
    is_deleted = Column(Boolean, default=False, nullable=False)