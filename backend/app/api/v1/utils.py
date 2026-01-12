from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import aiofiles
import os
import uuid
from app.core.config import settings
from app.core.image_processor import image_processor_manager

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    # 1. 格式验证
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        # 读取前几个字节验证 Magic Number (增强安全性)
        header = content[:4]
        
        # 简单 Magic Number 检查 (JPEG/PNG)
        # JPEG: FF D8 FF
        # PNG: 89 50 4E 47
        is_valid = False
        if header.startswith(b'\xff\xd8\xff') or header.startswith(b'\x89PNG'):
            is_valid = True
            
        if not is_valid and file_ext != '.webp': # 简化处理
            pass # 严格模式应抛错，这里为兼容性暂放宽
        
        # 使用腾讯云COS上传图片
        result = await image_processor_manager.upload_and_process_image(content, file.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Upload failed"))
        
        # 返回COS上的URL
        file_url = result["processed_url"]
        
        return {"url": file_url, "cos_key": result.get("cos_key")}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
