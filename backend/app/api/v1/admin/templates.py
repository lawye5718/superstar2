from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Any, Optional
from app.core.dependencies import get_db, get_current_active_user
from app.models import Template, User
from app.schemas import template as template_schemas
from app.models.database import GenderEnum
from app.core.image_processor import image_processor_manager

router = APIRouter()

@router.post("/", response_model=template_schemas.TemplateResponse)
def create_template(
    title: str = Form(...),
    gender: str = Form(...),
    tags: str = Form(...),  # 逗号分隔的标签
    price: float = Form(9.9),
    is_approved: bool = Form(False),
    config: str = Form(...),  # JSON字符串
    example_image: UploadFile = File(None),  # 实例图片
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permission denied")
    
    import json
    
    # 解析JSON字符串
    try:
        config_dict = json.loads(config)
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for config")
    
    # 处理上传的实例图片
    display_image_urls = []
    if example_image and example_image.filename:
        try:
            content = await example_image.read()
            result = await image_processor_manager.upload_and_process_image(
                content, example_image.filename)
            if result["success"]:
                display_image_urls.append(result["processed_url"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload example image: {str(e)}")
    
    template = Template(
        title=title,
        gender=gender,
        tags=tags_list,
        config=config_dict,
        price=price,
        is_approved=is_approved,
        display_image_urls=display_image_urls,
        usage_count=0
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{id}", response_model=dict)
def delete_template(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permission denied")
    template = db.query(Template).filter(Template.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(template)
    db.commit()
    return {"status": "success"}

@router.put("/{id}", response_model=template_schemas.TemplateResponse)
def update_template(
    id: int,
    title: str = Form(None),
    gender: str = Form(None),
    tags: str = Form(None),  # 逗号分隔的标签
    price: float = Form(None),
    is_approved: bool = Form(None),
    config: str = Form(None),  # JSON字符串
    example_image: UploadFile = File(None),  # 实例图片
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permission denied")
    
    template = db.query(Template).filter(Template.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    import json
    
    # 更新模板信息
    if title is not None:
        template.title = title
    if gender is not None:
        template.gender = gender
    if tags is not None:
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        template.tags = tags_list
    if price is not None:
        template.price = price
    if is_approved is not None:
        template.is_approved = is_approved
    if config is not None:
        try:
            config_dict = json.loads(config)
            template.config = config_dict
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for config")
    
    # 处理上传的实例图片
    if example_image and example_image.filename:
        try:
            content = await example_image.read()
            result = await image_processor_manager.upload_and_process_image(
                content, example_image.filename)
            if result["success"]:
                template.display_image_urls = [result["processed_url"]]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload example image: {str(e)}")
    
    db.commit()
    db.refresh(template)
    return template
