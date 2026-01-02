from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from enum import Enum

from app.schemas.flower import FlowerResponse
from app.schemas.customer import CustomerResponse


class OrderStatus(str, Enum):
    ORDERED = "ordered"
    DELIVERED = "delivered"


# Order Item schemas
class OrderItemBase(BaseModel):
    flower_id: int
    quantity: int = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(BaseModel):
    id: int
    flower_id: int
    quantity: int
    unit_price: Decimal
    flower: Optional[FlowerResponse] = None

    class Config:
        from_attributes = True


# Order schemas
class OrderBase(BaseModel):
    customer_id: int
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    total_price: Decimal
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    customer: Optional[CustomerResponse] = None
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    skip: int
    limit: int


