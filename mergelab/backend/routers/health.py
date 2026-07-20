from fastapi import APIRouter
from config import settings
import time
import os

router = APIRouter(prefix="/api", tags=["Health"])

START_TIME = time.time()


@router.get("/health")
async def health_check():
    """Check system health and status."""
    
    # Get disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(settings.STORAGE_PATH)
        disk_space_gb = total / (1024 ** 3)
        disk_free_gb = free / (1024 ** 3)
    except Exception:
        disk_space_gb = 0
        disk_free_gb = 0
    
    # Check GPU availability
    gpu_available = False
    try:
        import torch
        gpu_available = torch.cuda.is_available()
    except ImportError:
        pass
    
    # Count active jobs (in production, query from database)
    active_jobs = 0
    
    # Count cached models
    models_cached = 0
    cache_dir = os.path.join(settings.STORAGE_PATH, "cache", "models")
    if os.path.exists(cache_dir):
        models_cached = len([d for d in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, d))])
    
    uptime = int(time.time() - START_TIME)
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "gpu_available": gpu_available,
        "disk_space_gb": round(disk_space_gb, 2),
        "disk_free_gb": round(disk_free_gb, 2),
        "active_jobs": active_jobs,
        "models_cached": models_cached,
        "uptime_seconds": uptime
    }
