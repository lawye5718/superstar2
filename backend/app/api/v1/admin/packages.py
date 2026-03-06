from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Literal, Optional

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.models.database import Package, PackageTemplateRule, PackageRuleTypeEnum, User
from app.api.v1.admin.stats import _require_admin
from pydantic import BaseModel


class PackageRuleCreate(BaseModel):
    rule_type: Literal["FIXED", "RANDOM_TAG", "RANDOM_SET", "RANDOM_ALL"]
    rule_config: Dict[str, Any]
    template_id: Optional[str] = None


class AdminPackageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    item_count: int
    price: float
    default_display_image_url: Optional[str] = None
    is_active: bool = True
    rules: List[PackageRuleCreate] = []


class AdminPackageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    item_count: Optional[int] = None
    price: Optional[float] = None
    default_display_image_url: Optional[str] = None
    is_active: Optional[bool] = None


class PackageResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    item_count: int
    price: float
    default_display_image_url: Optional[str] = None
    is_active: bool
    rule_count: int

    class Config:
        from_attributes = True


RULE_TYPE_MAP = {
    "FIXED": PackageRuleTypeEnum.FIXED,
    "RANDOM_TAG": PackageRuleTypeEnum.RANDOM_TAG,
    "RANDOM_SET": PackageRuleTypeEnum.RANDOM_SET,
    "RANDOM_ALL": PackageRuleTypeEnum.RANDOM_ALL,
}

router = APIRouter()


@router.get("/", response_model=List[PackageResponse])
def list_packages_admin(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """List all packages for admin"""
    _require_admin(db, current_user_id)

    packages = (
        db.query(Package)
        .order_by(Package.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        PackageResponse(
            id=str(p.id),
            name=p.name,
            description=p.description,
            item_count=p.item_count,
            price=float(p.price),
            default_display_image_url=p.default_display_image_url,
            is_active=p.is_active,
            rule_count=len(p.rules),
        )
        for p in packages
    ]


@router.post("/", response_model=PackageResponse)
def create_package(
    package_in: AdminPackageCreate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """Create a new package (admin only)"""
    _require_admin(db, current_user_id)

    package = Package(
        name=package_in.name,
        description=package_in.description,
        item_count=package_in.item_count,
        price=package_in.price,
        default_display_image_url=package_in.default_display_image_url,
        is_active=package_in.is_active,
    )
    db.add(package)
    db.flush()

    for rule_in in package_in.rules:
        rule_type = RULE_TYPE_MAP.get(rule_in.rule_type)
        if not rule_type:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rule_type: {rule_in.rule_type}",
            )
        rule = PackageTemplateRule(
            package_id=package.id,
            rule_type=rule_type,
            rule_config=rule_in.rule_config,
            template_id=rule_in.template_id,
        )
        db.add(rule)

    db.commit()
    db.refresh(package)

    return PackageResponse(
        id=str(package.id),
        name=package.name,
        description=package.description,
        item_count=package.item_count,
        price=float(package.price),
        default_display_image_url=package.default_display_image_url,
        is_active=package.is_active,
        rule_count=len(package.rules),
    )


@router.put("/{package_id}", response_model=PackageResponse)
def update_package(
    package_id: str,
    package_in: AdminPackageUpdate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """Update a package (admin only)"""
    _require_admin(db, current_user_id)

    package = db.query(Package).filter(Package.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    if package_in.name is not None:
        package.name = package_in.name
    if package_in.description is not None:
        package.description = package_in.description
    if package_in.item_count is not None:
        package.item_count = package_in.item_count
    if package_in.price is not None:
        package.price = package_in.price
    if package_in.default_display_image_url is not None:
        package.default_display_image_url = package_in.default_display_image_url
    if package_in.is_active is not None:
        package.is_active = package_in.is_active

    db.commit()
    db.refresh(package)

    return PackageResponse(
        id=str(package.id),
        name=package.name,
        description=package.description,
        item_count=package.item_count,
        price=float(package.price),
        default_display_image_url=package.default_display_image_url,
        is_active=package.is_active,
        rule_count=len(package.rules),
    )


@router.delete("/{package_id}", response_model=PackageResponse)
def deactivate_package(
    package_id: str,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """Deactivate a package (admin only)"""
    _require_admin(db, current_user_id)

    package = db.query(Package).filter(Package.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    package.is_active = False
    db.commit()
    db.refresh(package)

    return PackageResponse(
        id=str(package.id),
        name=package.name,
        description=package.description,
        item_count=package.item_count,
        price=float(package.price),
        default_display_image_url=package.default_display_image_url,
        is_active=package.is_active,
        rule_count=len(package.rules),
    )
