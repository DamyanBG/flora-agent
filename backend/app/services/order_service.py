from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.models.flower import Flower
from app.models.customer import Customer
from app.schemas.order import (
    OrderCreate, 
    OrderStatusUpdate, 
    OrderResponse, 
    OrderListResponse,
    OrderItemResponse
)
from app.schemas.order import OrderStatus as OrderStatusEnum
from app.services.flower_service import FlowerService


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.flower_service = FlowerService(db)
    
    async def get_orders(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[OrderStatusEnum] = None
    ) -> OrderListResponse:
        """Get all orders with pagination, optionally filtered by status."""
        # Build base query
        query = select(Order).options(
            selectinload(Order.customer),
            selectinload(Order.items).selectinload(OrderItem.flower)
        )
        count_query = select(func.count()).select_from(Order)
        
        # Apply status filter if provided
        if status:
            query = query.where(Order.status == status.value)
            count_query = count_query.where(Order.status == status.value)
        
        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get paginated orders
        result = await self.db.execute(
            query.order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = result.scalars().all()
        
        return OrderListResponse(
            items=[self._to_order_response(o) for o in orders],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get an order by ID with related data."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.customer),
                selectinload(Order.items).selectinload(OrderItem.flower)
            )
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """Create a new order with items."""
        # Verify customer exists
        customer_result = await self.db.execute(
            select(Customer).where(Customer.id == order_data.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate and calculate order items
        total_price = Decimal("0.00")
        order_items_data = []
        
        for item in order_data.items:
            # Get flower and validate
            flower = await self.flower_service.get_flower_by_id(item.flower_id)
            if not flower:
                raise ValueError(f"Flower with ID {item.flower_id} not found")
            
            # Check stock availability
            if flower.stock_quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {flower.name}. "
                    f"Available: {flower.stock_quantity}, Requested: {item.quantity}"
                )
            
            # Calculate item price
            item_price = flower.price * item.quantity
            total_price += item_price
            
            order_items_data.append({
                "flower_id": item.flower_id,
                "quantity": item.quantity,
                "unit_price": flower.price,
                "flower": flower
            })
        
        # Create order
        order = Order(
            customer_id=order_data.customer_id,
            status=OrderStatus.ORDERED.value,
            total_price=total_price,
            notes=order_data.notes
        )
        self.db.add(order)
        await self.db.flush()
        
        # Create order items and reduce stock
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                flower_id=item_data["flower_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"]
            )
            self.db.add(order_item)
            
            # Reduce stock
            await self.flower_service.reduce_stock(
                item_data["flower_id"], 
                item_data["quantity"]
            )
        
        await self.db.flush()
        
        # Reload order with relationships
        return await self.get_order_by_id(order.id)
    
    async def update_order_status(
        self, 
        order_id: int, 
        status_data: OrderStatusUpdate
    ) -> Optional[Order]:
        """Update order status."""
        order = await self.get_order_by_id(order_id)
        if not order:
            return None
        
        order.status = status_data.status.value
        await self.db.flush()
        
        # Reload to get updated data
        return await self.get_order_by_id(order_id)
    
    async def delete_order(self, order_id: int) -> bool:
        """Delete an order and restore stock."""
        order = await self.get_order_by_id(order_id)
        if not order:
            return False
        
        # Restore stock for each item
        for item in order.items:
            flower = await self.flower_service.get_flower_by_id(item.flower_id)
            if flower:
                flower.stock_quantity += item.quantity
        
        # Delete order (cascade will delete items)
        await self.db.delete(order)
        await self.db.flush()
        
        return True
    
    async def get_orders_by_customer(
        self, 
        customer_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> OrderListResponse:
        """Get all orders for a specific customer."""
        # Get total count
        count_result = await self.db.execute(
            select(func.count())
            .select_from(Order)
            .where(Order.customer_id == customer_id)
        )
        total = count_result.scalar()
        
        # Get paginated orders
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.customer),
                selectinload(Order.items).selectinload(OrderItem.flower)
            )
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = result.scalars().all()
        
        return OrderListResponse(
            items=[self._to_order_response(o) for o in orders],
            total=total,
            skip=skip,
            limit=limit
        )
    
    def _to_order_response(self, order: Order) -> OrderResponse:
        """Convert Order model to OrderResponse schema."""
        return OrderResponse(
            id=order.id,
            customer_id=order.customer_id,
            status=OrderStatusEnum(order.status),
            total_price=order.total_price,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            customer=order.customer,
            items=[
                OrderItemResponse(
                    id=item.id,
                    flower_id=item.flower_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    flower=item.flower
                )
                for item in order.items
            ]
        )


