from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_customers(self, skip: int = 0, limit: int = 100) -> CustomerListResponse:
        """Get all customers with pagination."""
        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(Customer))
        total = count_result.scalar()
        
        # Get paginated customers
        result = await self.db.execute(
            select(Customer)
            .order_by(Customer.last_name, Customer.first_name)
            .offset(skip)
            .limit(limit)
        )
        customers = result.scalars().all()
        
        return CustomerListResponse(
            items=[CustomerResponse.model_validate(c) for c in customers],
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get a customer by email."""
        result = await self.db.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create a new customer."""
        customer = Customer(**customer_data.model_dump())
        self.db.add(customer)
        
        try:
            await self.db.flush()
            await self.db.refresh(customer)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Customer with this email already exists")
        
        return customer
    
    async def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        """Update a customer."""
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        try:
            await self.db.flush()
            await self.db.refresh(customer)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Customer with this email already exists")
        
        return customer
    
    async def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer."""
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            return False
        
        # Check if customer has orders
        if customer.orders:
            return False  # Cannot delete customer with existing orders
        
        await self.db.delete(customer)
        await self.db.flush()
        
        return True
    
    async def search_customers(self, query: str, skip: int = 0, limit: int = 100) -> CustomerListResponse:
        """Search customers by name or email."""
        search_pattern = f"%{query}%"
        
        # Get total count for search
        count_result = await self.db.execute(
            select(func.count()).select_from(Customer).where(
                (Customer.first_name.ilike(search_pattern)) |
                (Customer.last_name.ilike(search_pattern)) |
                (Customer.email.ilike(search_pattern))
            )
        )
        total = count_result.scalar()
        
        # Get paginated search results
        result = await self.db.execute(
            select(Customer)
            .where(
                (Customer.first_name.ilike(search_pattern)) |
                (Customer.last_name.ilike(search_pattern)) |
                (Customer.email.ilike(search_pattern))
            )
            .order_by(Customer.last_name, Customer.first_name)
            .offset(skip)
            .limit(limit)
        )
        customers = result.scalars().all()
        
        return CustomerListResponse(
            items=[CustomerResponse.model_validate(c) for c in customers],
            total=total,
            skip=skip,
            limit=limit
        )


