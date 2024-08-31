from .basic_import import *
from database.db import BASE
class AuthKeys(BASE):
    __tablename__ = 'tbl_auth_keys'
    key_id = Column(Integer, primary_key=True, index=True)
    key_value = Column(String(20), unique=True, index=True)
    key_valid_till = Column(DateTime)
    is_active = Column(Boolean, default=True)
    subscriber_id = Column(Integer,default=0)