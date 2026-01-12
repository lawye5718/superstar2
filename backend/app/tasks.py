"""Celery tasks configuration and task definitions"""

from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "superstar",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


@celery_app.task(bind=True, name="tasks.generate_image")
def generate_image_task(self, task_id: str):
    """
    Celery task for generating AI images.
    
    Args:
        task_id: The ID of the GenerationTask to process
    
    Returns:
        dict: Result containing success status and data
    """
    from app.core.database import SessionLocal
    from app.models.database import GenerationTask, TaskStatusEnum, UserGallery
    from app.services.gallery_service import GalleryService
    import logging
    
    logger = logging.getLogger(__name__)
    db = SessionLocal()
    
    try:
        # Update task status to PROCESSING
        task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return {"success": False, "error": "Task not found"}
        
        task.status = TaskStatusEnum.PROCESSING
        db.commit()
        
        logger.info(f"Processing task {task_id} for user {task.user_id}")
        
        # Generate the image using GalleryService
        gallery_service = GalleryService(db)
        
        # For now, create a placeholder gallery item
        # In production, this would call the actual AI image generation service
        gallery_item = UserGallery(
            user_id=task.user_id,
            template_id=task.template_id,
            image_url_free=task.portrait_url or "https://via.placeholder.com/1080x1080?text=Generated+Image",
            image_url_paid=None,
            thumbnail_url=None,
            is_public=False
        )
        db.add(gallery_item)
        db.flush()
        
        # Update task with result
        task.status = TaskStatusEnum.COMPLETED
        task.result_gallery_id = gallery_item.id
        db.commit()
        
        logger.info(f"Task {task_id} completed successfully")
        return {
            "success": True,
            "task_id": task_id,
            "gallery_id": str(gallery_item.id)
        }
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
        
        # Update task status to FAILED
        if task:
            task.status = TaskStatusEnum.FAILED
            task.error_message = str(e)
            db.commit()
        
        return {"success": False, "error": str(e)}
        
    finally:
        db.close()


@celery_app.task(name="tasks.cleanup_old_tasks")
def cleanup_old_tasks():
    """
    Periodic task to cleanup old completed/failed tasks.
    Run daily to maintain database performance.
    """
    from app.core.database import SessionLocal
    from app.models.database import GenerationTask, TaskStatusEnum
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    db = SessionLocal()
    
    try:
        # Delete tasks older than 30 days that are completed or failed
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        deleted_count = db.query(GenerationTask).filter(
            GenerationTask.created_at < cutoff_date,
            GenerationTask.status.in_([TaskStatusEnum.COMPLETED, TaskStatusEnum.FAILED])
        ).delete(synchronize_session=False)
        
        db.commit()
        logger.info(f"Cleaned up {deleted_count} old tasks")
        
        return {"success": True, "deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Error cleaning up old tasks: {str(e)}", exc_info=True)
        db.rollback()
        return {"success": False, "error": str(e)}
        
    finally:
        db.close()
