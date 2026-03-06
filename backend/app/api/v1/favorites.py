from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.models.database import TemplateFavorite, Template

from app.schemas.template import TemplateResponse

router = APIRouter()


@router.post("/{template_id}/favorite")
def toggle_favorite(
    template_id: str,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """Toggle favorite on a template (add if not exists, remove if exists)."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    existing = (
        db.query(TemplateFavorite)
        .filter(
            TemplateFavorite.user_id == current_user_id,
            TemplateFavorite.template_id == template_id,
        )
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()
        return {"is_favorited": False}

    fav = TemplateFavorite(user_id=current_user_id, template_id=template_id)
    db.add(fav)
    db.commit()
    return {"is_favorited": True}


@router.delete("/{template_id}/favorite")
def remove_favorite(
    template_id: str,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """Remove a template from favorites."""
    existing = (
        db.query(TemplateFavorite)
        .filter(
            TemplateFavorite.user_id == current_user_id,
            TemplateFavorite.template_id == template_id,
        )
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(existing)
    db.commit()
    return {"is_favorited": False}


@router.get("/", response_model=List[TemplateResponse])
def list_favorites(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """List current user's favorited templates."""
    favs = (
        db.query(TemplateFavorite)
        .filter(TemplateFavorite.user_id == current_user_id)
        .order_by(TemplateFavorite.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    template_ids = [f.template_id for f in favs]
    if not template_ids:
        return []

    templates = db.query(Template).filter(Template.id.in_(template_ids)).all()
    templates_by_id = {str(t.id): t for t in templates}

    result = []
    for fav in favs:
        t = templates_by_id.get(str(fav.template_id))
        if not t:
            continue
        result.append(
            TemplateResponse(
                id=str(t.id),
                title=t.title,
                gender=t.gender,
                tags=t.tags or [],
                config=t.config or {},
                is_approved=t.is_approved,
                display_image_urls=t.display_image_urls or [],
                price=float(t.price) if t.price else None,
                usage_count=t.usage_count or 0,
                is_favorited=True,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
        )
    return result
