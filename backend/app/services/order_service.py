# 新建文件: backend/app/services/order_service.py
from sqlalchemy.orm import Session
from app.models.database import User, Template, Order, OrderStatusEnum
from app.core.config import settings
from fastapi import HTTPException
import uuid

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order_with_transaction(self, user_id: str, template_id: str) -> Order:
        """创建订单并扣款，包含完整的事务处理"""
        try:
            # ✅ 开启显式事务
            with self.db.begin():
                # ✅ 关键修复：使用 with_for_update() 锁定用户行，防止并发扣款
                user = self.db.query(User).filter(User.id == user_id).with_for_update().first()
                if not user:
                    raise HTTPException(404, "User not found")
                
                template = self.db.query(Template).filter(Template.id == template_id).first()
                if not template:
                    raise HTTPException(404, "Template not found")

                # 计算价格
                price = float(template.price) if hasattr(template, 'price') and template.price else settings.DEFAULT_TEMPLATE_PRICE
                
                # 检查余额
                if user.credits < price:
                    raise HTTPException(400, "Insufficient balance")

                # 执行扣款
                user.credits -= price
                
                # 创建订单
                order = Order(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    template_id=template_id,
                    amount=price,
                    credits_consumed=price,
                    credits_purchased=0,
                    status=OrderStatusEnum.COMPLETED, # 或 PENDING，视业务而定
                    platform="web",
                    result_image_url=template.display_image_urls[0] if template.display_image_urls else settings.DEFAULT_RESULT_IMAGE_PLACEHOLDER
                )
                self.db.add(order)
                
                # 更新模板统计
                template.usage_count = (template.usage_count or 0) + 1
                
                return order
                # with 块结束时自动 commit，失败自动 rollback
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Order transaction failed: {str(e)}")