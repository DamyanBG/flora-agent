from fastapi import APIRouter, HTTPException, status, Query

from app.core.dependencies import DbSession, CurrentUser
from app.schemas.flower import (
    FlowerCreate, 
    FlowerUpdate, 
    FlowerStockUpdate, 
    FlowerResponse, 
    FlowerListResponse
)
from app.services.flower_service import FlowerService

router = APIRouter()


@router.get("", response_model=FlowerListResponse)
async def list_flowers(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    """
    Get all flowers with pagination.
    Results are cached for 5 minutes.
    """
    service = FlowerService(db)
    return await service.get_flowers(skip=skip, limit=limit)


@router.get("/{flower_id}", response_model=FlowerResponse)
async def get_flower(
    flower_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Get a flower by ID.
    """
    service = FlowerService(db)
    flower = await service.get_flower_by_id(flower_id)
    
    if not flower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flower not found"
        )
    
    return flower


@router.post("", response_model=FlowerResponse, status_code=status.HTTP_201_CREATED)
async def create_flower(
    flower_data: FlowerCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Create a new flower.
    """
    service = FlowerService(db)
    return await service.create_flower(flower_data)


@router.put("/{flower_id}", response_model=FlowerResponse)
async def update_flower(
    flower_id: int,
    flower_data: FlowerUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Update a flower.
    """
    service = FlowerService(db)
    flower = await service.update_flower(flower_id, flower_data)
    
    if not flower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flower not found"
        )
    
    return flower


@router.patch("/{flower_id}/stock", response_model=FlowerResponse)
async def update_flower_stock(
    flower_id: int,
    stock_data: FlowerStockUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Update flower stock quantity.
    """
    service = FlowerService(db)
    flower = await service.update_stock(flower_id, stock_data)
    
    if not flower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flower not found"
        )
    
    return flower


@router.delete("/{flower_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flower(
    flower_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Delete a flower.
    Cannot delete flowers that are used in existing orders.
    """
    service = FlowerService(db)
    deleted = await service.delete_flower(flower_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Flower not found or cannot be deleted (used in existing orders)"
        )
