from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional


class FlowerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)


class FlowerCreate(FlowerBase):
    pass


class FlowerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)


class FlowerStockUpdate(BaseModel):
    stock_quantity: int = Field(..., ge=0)


class FlowerResponse(FlowerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FlowerListResponse(BaseModel):
    items: list[FlowerResponse]
    total: int
    skip: int
    limit: int


