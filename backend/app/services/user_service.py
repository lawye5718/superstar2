"""User service"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.database import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_in: UserCreate):
        """Create a new user"""
        # Hash the password
        hashed_password = get_password_hash(user_in.password)
        
        # Create user instance
        db_user = User(
            email=user_in.email,
            password_hash=hashed_password,
            balance=0,  # Default balance
            roles=["user"]  # Default role
        )
        
        # Add to database
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: str, user_in: UserUpdate) -> Optional[User]:
        """Update user by ID"""
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return None

        # Update fields if provided
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return False

        await self.db.delete(db_user)
        await self.db.commit()
        return True