from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import aiofiles  # 需要安装 aiofiles: pip install aiofiles
import os
import uuid

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/upload", response_model=dict)
async def upload_file(
    request: Request,
    file: UploadFile = File(...)
):
    """
    通用文件上传接口 (支持 Admin 上传模版图 & 用户上传头像)
    """
    # 1. 验证图片格式
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # 2. Read in chunks and enforce size limit before writing
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, new_filename)

    chunk_size = 1024 * 64  # 64 KB
    total_size = 0
    chunks: list[bytes] = []
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        chunks.append(chunk)

    # 3. 确保存储目录存在 (already done above)
    # 4. 异步写入文件
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            for chunk in chunks:
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
        
    # 5. 动态生成 URL (解决 localhost 硬编码问题)
    # request.base_url 会自动根据访问的域名/IP变化
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/{upload_dir}/{new_filename}"
    
    return {"url": file_url}