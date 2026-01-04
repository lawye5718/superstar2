"""Order service"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import Order
from app.schemas.order import OrderCreate


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order_in: OrderCreate):
        """Create a new order"""
        db_order = Order(
            user_id=order_in.user_id,
            credits_purchased=order_in.credits_purchased,
            amount=order_in.amount,
            platform=order_in.platform,
            status=order_in.status
        )
        
        self.db.add(db_order)
        await self.db.commit()
        await self.db.refresh(db_order)
        
        return db_order

    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders with pagination"""
        result = await self.db.execute(
            select(Order).offset(skip).limit(limit)
        )
        return result.scalars().all()