"""Order API routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new order"""
    order_service = OrderService(db)
    order = await order_service.create_order(order_in)
    return order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get orders with pagination"""
    order_service = OrderService(db)
    orders = await order_service.get_orders(skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get order by ID"""
    order_service = OrderService(db)
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order