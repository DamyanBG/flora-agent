from fastapi import APIRouter

from app.api.v1 import auth, flowers, customers, orders

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(flowers.router, prefix="/flowers", tags=["Flowers"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])


