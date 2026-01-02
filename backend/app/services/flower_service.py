from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.flower import Flower
from app.schemas.flower import FlowerCreate, FlowerUpdate, FlowerStockUpdate, FlowerResponse, FlowerListResponse
from app.utils.cache import get_cached, set_cached, get_flowers_list_key, invalidate_flowers_cache


class FlowerService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_flowers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        use_cache: bool = True
    ) -> FlowerListResponse:
        """Get all flowers with pagination, optionally from cache."""
        cache_key = get_flowers_list_key(skip, limit)
        
        # Try to get from cache
        if use_cache:
            cached = await get_cached(cache_key)
            if cached:
                return FlowerListResponse(**cached)
        
        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(Flower))
        total = count_result.scalar()
        
        # Get paginated flowers
        result = await self.db.execute(
            select(Flower)
            .order_by(Flower.name)
            .offset(skip)
            .limit(limit)
        )
        flowers = result.scalars().all()
        
        # Build response
        response = FlowerListResponse(
            items=[FlowerResponse.model_validate(f) for f in flowers],
            total=total,
            skip=skip,
            limit=limit
        )
        
        # Cache the result
        if use_cache:
            await set_cached(cache_key, response.model_dump())
        
        return response
    
    async def get_flower_by_id(self, flower_id: int) -> Optional[Flower]:
        """Get a flower by ID."""
        result = await self.db.execute(
            select(Flower).where(Flower.id == flower_id)
        )
        return result.scalar_one_or_none()
    
    async def create_flower(self, flower_data: FlowerCreate) -> Flower:
        """Create a new flower."""
        flower = Flower(**flower_data.model_dump())
        self.db.add(flower)
        await self.db.flush()
        await self.db.refresh(flower)
        
        # Invalidate cache
        await invalidate_flowers_cache()
        
        return flower
    
    async def update_flower(self, flower_id: int, flower_data: FlowerUpdate) -> Optional[Flower]:
        """Update a flower."""
        flower = await self.get_flower_by_id(flower_id)
        if not flower:
            return None
        
        update_data = flower_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(flower, field, value)
        
        await self.db.flush()
        await self.db.refresh(flower)
        
        # Invalidate cache
        await invalidate_flowers_cache()
        
        return flower
    
    async def update_stock(self, flower_id: int, stock_data: FlowerStockUpdate) -> Optional[Flower]:
        """Update flower stock quantity."""
        flower = await self.get_flower_by_id(flower_id)
        if not flower:
            return None
        
        flower.stock_quantity = stock_data.stock_quantity
        await self.db.flush()
        await self.db.refresh(flower)
        
        # Invalidate cache
        await invalidate_flowers_cache()
        
        return flower
    
    async def delete_flower(self, flower_id: int) -> bool:
        """Delete a flower."""
        flower = await self.get_flower_by_id(flower_id)
        if not flower:
            return False
        
        # Check if flower is used in any orders
        if flower.order_items:
            return False  # Cannot delete flower with existing orders
        
        await self.db.delete(flower)
        await self.db.flush()
        
        # Invalidate cache
        await invalidate_flowers_cache()
        
        return True
    
    async def check_stock_availability(self, flower_id: int, quantity: int) -> bool:
        """Check if flower has sufficient stock."""
        flower = await self.get_flower_by_id(flower_id)
        if not flower:
            return False
        return flower.stock_quantity >= quantity
    
    async def reduce_stock(self, flower_id: int, quantity: int) -> bool:
        """Reduce flower stock by quantity."""
        flower = await self.get_flower_by_id(flower_id)
        if not flower or flower.stock_quantity < quantity:
            return False
        
        flower.stock_quantity -= quantity
        await self.db.flush()
        
        # Invalidate cache
        await invalidate_flowers_cache()
        
        return True


