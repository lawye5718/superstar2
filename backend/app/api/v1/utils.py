from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import aiofiles  # 需要安装 aiofiles: pip install aiofiles
import os
import uuid

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_file(
    request: Request,
    file: UploadFile = File(...)
):
    """
    通用文件上传接口 (支持 Admin 上传模版图 & 用户上传头像)
    """
    # 1. 验证图片格式和扩展名
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if not file.content_type.startswith('image/') or file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File must be an image (jpg, jpeg, png, webp, gif)")
    
    # 2. 限制文件大小 (10MB)
    max_file_size = 10 * 1024 * 1024  # 10MB in bytes
    # Note: We can't know the full file size until we start reading it, 
    # so we'll check during the read process
    
    # 2. 确保存储目录存在
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 3. 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, new_filename)
    
    # 4. 异步写入文件 (解决阻塞问题) + 文件大小限制
    total_size = 0
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            # 分块读取，防止内存溢出
            while content := await file.read(1024 * 1024):  # 1MB chunks
                total_size += len(content)
                if total_size > max_file_size:
                    raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
        
    # ✅ 修复：强制返回 localhost 或者相对路径
    # 在 Web 环境中，前端通常访问 http://localhost:8000/static/...
    file_url = f"http://localhost:8000/{upload_dir}/{new_filename}"
    
    return {"url": file_url}