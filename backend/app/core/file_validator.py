# 新建文件: backend/app/core/file_validator.py
import imghdr
import os
from typing import Tuple

# 允许的扩展名白名单
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
# 文件大小限制 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_uploaded_file(filename: str, content: bytes) -> str:
    """
    验证上传文件的安全：大小、扩展名、魔数
    返回: 标准化的文件扩展名
    """
    # 1. 验证大小
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)}MB")

    # 2. 验证扩展名
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # 3. 验证魔数 (文件头)
    image_type = imghdr.what(None, h=content)
    if not image_type:
        raise ValueError("Invalid image content (Magic number mismatch)")
    
    return ext