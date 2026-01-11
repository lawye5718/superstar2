from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import aiofiles
import os
import uuid
from app.core.config import settings

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # 兼容 Docker 路径
    upload_dir = "static/uploads"
    full_path = "/app/static/uploads" if os.path.exists("/app") else "static/uploads"
    os.makedirs(full_path, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(full_path, new_filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")
    
    # ✅ 修复：使用配置文件中的域名
    file_url = f"{settings.DOMAIN}/static/uploads/{new_filename}"
    
    return {"url": file_url}
