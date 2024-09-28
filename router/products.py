from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from .basic_import import *
from models.products import Products 
from router.login import check_auth_key

Products.metadata.create_all(engine)

router = APIRouter()

class ProductBase(BaseModel):
    product_name: str
    product_description: str
    product_image_url: str
    product_url:str
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)

@router.post("/create-product/")
async def create_product(product_data: ProductBase, db: db_dependency):
    try:
        product = Products(**product_data.dict())
        db.add(product)
        db.commit()
        db.refresh(product)
        return succes_response(product, "Product created successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.get("/get-product/{product_id}/")
async def get_product_by_id(product_id: int, db: db_dependency):
    product = db.query(Products).filter(
        Products.product_id == product_id,
        Products.is_deleted == False
    ).first()
    if product is None:
        raise raise_exception(404, "Product not found")
    return jsonable_encoder(product)

@router.get("/get-all-products/")
async def get_product_by_id(db: db_dependency):
    products = db.query(Products).filter(
        Products.is_deleted == False
    ).all()
    return jsonable_encoder(products)

@router.delete("/delete-product/{product_id}/")
async def delete_product(product_id: int, db: db_dependency):
    product = db.query(Products).filter(Products.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product.is_deleted = True
        db.commit()
        return succes_response(None, "Product deleted successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")

@router.patch("/update-product/")
async def update_product(product_data: ProductBase,product_id: int ,db: db_dependency):
    product = await check_instance(Products,"product_id",product_id,db)
    if product is None:
        raise raise_exception(404,"Product not found")
    try:
        for key,val in product_data.__dict__.items():
            if val:
                setattr(product,key,val)
        db.commit()
        db.refresh(product)
        return succes_response(product, "Product updated successfully")
    except Exception as e:
        raise raise_exception(500, f"Internal Server Error: {e}")