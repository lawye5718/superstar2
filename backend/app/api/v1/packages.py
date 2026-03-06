"""User-facing package API routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from pydantic import BaseModel

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.models.database import Package, Order, OrderStatusEnum, User

router = APIRouter()


class PackageListItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    item_count: int
    price: float
    default_display_image_url: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PackageListItem])
def list_active_packages(
    db: Session = Depends(get_sync_db),
) -> Any:
    """List active packages for users to browse"""
    packages = (
        db.query(Package)
        .filter(Package.is_active == True)
        .order_by(Package.price.asc())
        .all()
    )
    return [
        PackageListItem(
            id=str(p.id),
            name=p.name,
            description=p.description,
            item_count=p.item_count,
            price=float(p.price),
            default_display_image_url=p.default_display_image_url,
        )
        for p in packages
    ]


@router.post("/{package_id}/purchase")
def purchase_package(
    package_id: str,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """Purchase a package (deduct credits, add to user orders)"""
    package = db.query(Package).filter(Package.id == package_id, Package.is_active == True).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found or inactive")

    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    package_price = float(package.price)
    current_balance = float(user.credits or 0)

    if current_balance < package_price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    user.credits = current_balance - package_price

    import uuid
    order = Order(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        package_id=package_id,
        status=OrderStatusEnum.COMPLETED,
        amount=package_price,
        credits_consumed=package_price,
        credits_purchased=package.item_count,
        platform="web",
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    db.refresh(user)

    return {
        "status": "success",
        "order_id": str(order.id),
        "package_name": package.name,
        "credits_remaining": float(user.credits),
    }
