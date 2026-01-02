from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.core.dependencies import DbSession, CurrentUser
from app.schemas.order import (
    OrderCreate,
    OrderStatusUpdate,
    OrderResponse,
    OrderListResponse,
    OrderStatus
)
from app.services.order_service import OrderService

router = APIRouter()


@router.get("", response_model=OrderListResponse)
async def list_orders(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    status: Optional[OrderStatus] = Query(default=None),
    customer_id: Optional[int] = Query(default=None),
):
    """
    Get all orders with pagination.
    Optionally filter by status or customer.
    """
    service = OrderService(db)
    
    if customer_id:
        return await service.get_orders_by_customer(customer_id, skip=skip, limit=limit)
    
    return await service.get_orders(skip=skip, limit=limit, status=status)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Get an order by ID with all items.
    """
    service = OrderService(db)
    order = await service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return service._to_order_response(order)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Create a new order.
    Validates customer exists and checks stock availability for all items.
    Stock is automatically reduced upon order creation.
    """
    service = OrderService(db)
    
    try:
        order = await service.create_order(order_data)
        return service._to_order_response(order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Update order status.
    Valid statuses: ordered, delivered
    """
    service = OrderService(db)
    order = await service.update_order_status(order_id, status_data)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return service._to_order_response(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Delete an order.
    Stock is automatically restored for all items.
    """
    service = OrderService(db)
    deleted = await service.delete_order(order_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
