from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.core.dependencies import DbSession, CurrentUser
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse
)
from app.services.customer_service import CustomerService

router = APIRouter()


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    search: Optional[str] = Query(default=None, min_length=1),
):
    """
    Get all customers with pagination.
    Optionally search by name or email.
    """
    service = CustomerService(db)
    
    if search:
        return await service.search_customers(search, skip=skip, limit=limit)
    
    return await service.get_customers(skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Get a customer by ID.
    """
    service = CustomerService(db)
    customer = await service.get_customer_by_id(customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Create a new customer.
    """
    service = CustomerService(db)
    
    try:
        return await service.create_customer(customer_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Update a customer.
    """
    service = CustomerService(db)
    
    try:
        customer = await service.update_customer(customer_id, customer_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Delete a customer.
    Cannot delete customers with existing orders.
    """
    service = CustomerService(db)
    deleted = await service.delete_customer(customer_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer not found or cannot be deleted (has existing orders)"
        )
