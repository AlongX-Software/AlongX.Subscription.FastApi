from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from .basic_import import *
from models.products import Products 

router = APIRouter()

class ProductBase(BaseModel):
    product_name: str
    product_description: str
    product_image_url: str
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
async def get_product(product_id: int, db: db_dependency):
    product = db.query(Products).filter(Products.product_id == product_id, Products.is_deleted == False).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "success", "data": product}

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
