"""
Image Processing Module for Volcano Engine and Tencent Cloud COS
移植自 superstar_tester/app.py 与火山引擎文档
"""

import os
import uuid
import base64
import httpx
import aiofiles
from typing import List, Dict, Any, Optional
from qcloud_cos import CosConfig, CosS3Client
from app.core.config import settings

# --- 1. 腾讯云 COS 客户端 (移植并优化) ---
class TencentCOSClient:
    """腾讯云COS客户端 - 负责文件存储"""
    
    def __init__(self):
        # 优先从 settings 读取，环境变量作为兜底
        self.secret_id = settings.COS_SECRET_ID or os.getenv("COS_SECRET_ID")
        self.secret_key = settings.COS_SECRET_KEY or os.getenv("COS_SECRET_KEY")
        self.region = settings.COS_REGION or os.getenv("COS_REGION", "ap-beijing")
        self.bucket = settings.COS_BUCKET or os.getenv("COS_BUCKET")
        
        if self.secret_id and self.secret_key and self.bucket:
            self.cos_config = CosConfig(
                Region=self.region,
                SecretId=self.secret_id,
                SecretKey=self.secret_key,
                Token=None,
                Scheme='https'
            )
            self.client = CosS3Client(self.cos_config)
            self.enabled = True
        else:
            print("警告: COS 配置缺失，存储功能将不可用。")
            self.enabled = False
    
    def _generate_cos_key(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1]
        # 统一存储路径结构
        return f"templates/{uuid.uuid4()}{ext}"
    
    async def upload_image_bytes(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"success": False, "error": "COS configuration not set"}
        
        try:
            cos_key = self._generate_cos_key(filename)
            #同步 SDK 调用，但在 FastAPI 线程池中运行是安全的，或者封装为 run_in_executor
            self.client.put_object(
                Bucket=self.bucket,
                Body=image_bytes,
                Key=cos_key,
                StorageClass='STANDARD'
            )
            
            url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_key}"
            return {
                "success": True,
                "url": url,
                "cos_key": cos_key
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# --- 2. 火山引擎处理器 (移植并优化) ---
class VolcEngineProcessor:
    """火山引擎处理器 - 负责 AI 作图"""
    
    def __init__(self):
        # 配置应从 config.py 统一管理
        self.api_url = settings.VOLC_API_URL # e.g. https://ark.cn-beijing.volces.com/api/v3/images/generations
        self.model_id = settings.VOLC_MODEL_ID
        self.api_key = settings.VOLC_API_KEY

    async def process_image_generation(self, prompt: str, reference_image_bytes: bytes, 
                                     size: str = "1024x1024", negative_prompt: str = "") -> Dict[str, Any]:
        """
        调用火山引擎进行单图生成 (Mode A)
        逻辑源自 superstar_tester/app.py
        """
        if not all([self.api_url, self.model_id, self.api_key]):
             return {"success": False, "error": "Volcano Engine configuration missing"}

        # 1. 转换参考图为 Base64 Data URI
        try:
            raw_base64 = base64.b64encode(reference_image_bytes).decode('utf-8')
            # 简单判断 MIME，生产环境可用 python-magic
            mime_type = "image/jpeg" 
            reference_data_uri = f"data:{mime_type};base64,{raw_base64}"
        except Exception as e:
            return {"success": False, "error": f"Image encoding failed: {str(e)}"}

        # 2. 构建 Payload (严格遵循 PDF 文档)
        payload = {
            "model": self.model_id,
            "prompt": prompt,
            "image": reference_data_uri,
            "size": size,
            "response_format": "url",
            "watermark": False,
            "stream": False,
            "sequential_image_generation": "disabled" # 强制单图模式
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 3. 异步请求
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "data" in data and len(data["data"]) > 0:
                    image_url = data["data"][0].get("url")
                    return {
                        "success": True,
                        "processed_url": image_url,
                        "usage": data.get("usage", {})
                    }
                else:
                    return {"success": False, "error": f"API Error: {data.get('error', {}).get('message', 'Unknown')}"}
            except Exception as e:
                return {"success": False, "error": f"Network Error: {str(e)}"}

# --- 3. 统一管理器 ---
class ImageProcessorManager:
    def __init__(self):
        self.volc_processor = VolcEngineProcessor()
        self.cos_client = TencentCOSClient()
    
    async def upload_example_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """专门用于管理员上传模版示例图到 COS"""
        return await self.cos_client.upload_image_bytes(file_content, filename)

    async def generate_and_upload(self, prompt: str, ref_bytes: bytes) -> Dict[str, Any]:
        """用户生成流程：调用火山 -> (可选：下载并转存 COS) -> 返回 URL"""
        # 第一步：火山生成
        gen_result = await self.volc_processor.process_image_generation(prompt, ref_bytes)
        if not gen_result["success"]:
            return gen_result
        
        # 优化点：如果需要长期保存用户生成的图片，这里应该下载 gen_result['processed_url'] 并上传到 COS
        # 目前先直接返回火山 URL (火山 URL 通常有有效期，建议后续增加转存逻辑)
        return gen_result

image_processor_manager = ImageProcessorManager()