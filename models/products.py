from .basic_import import *

class Products(BASE):
    __tablename__ = "tbl_products"
    product_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_name = Column(Text)
    product_description = Column(Text,nullable=True)
    product_image_url = Column(Text)
    product_url = Column(Text)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)