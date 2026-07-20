from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import asyncio
from datetime import datetime

from database import get_db, MergeJob
from schemas import (
    MergeRequest, MergeResponse, JobStatus, JobResult,
    TestRequest, TestResponse, DeployRequest, DeployResponse,
    HFPushRequest, HFPushResponse
)
from services.merge_engine import MergeEngine
from services.quantizer import Quantizer
from services.model_downloader import ModelDownloader
from services.hash_service import HashService
from services.hf_pusher import HFPusher
from services.test_runner import TestRunner
from config import settings

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/merge", tags=["Merge"])

# Global job status tracking (in production, use Redis)
active_jobs = {}


async def run_merge_job(
    job_id: str,
    model_a: str,
    model_b: str,
    method: str,
    ratio: float,
    output_format: str,
    output_name: str,
    db: Session
):
    """Background task to run merge job."""
    
    try:
        # Update job status
        job = db.query(MergeJob).filter(MergeJob.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Initialize services
        downloader = ModelDownloader(settings.STORAGE_PATH, settings.HF_TOKEN)
        merge_engine = MergeEngine(settings.STORAGE_PATH)
        quantizer = Quantizer(settings.STORAGE_PATH)
        hash_service = HashService()
        
        def progress_callback(step: str, percent: int):
            """Update job progress."""
            job.current_step = step
            job.progress_percent = percent
            job.status = "processing"
            db.commit()
            
            # Store in active jobs for SSE
            if job_id in active_jobs:
                active_jobs[job_id]["progress"] = percent
                active_jobs[job_id]["step"] = step
        
        # Step 1: Download models
        job.status = "downloading"
        job.current_step = f"Downloading {model_a}..."
        job.progress_percent = 10
        db.commit()
        
        path_a = downloader.download_from_hf(model_a, progress_callback=progress_callback)
        
        job.current_step = f"Downloading {model_b}..."
        job.progress_percent = 25
        db.commit()
        
        path_b = downloader.download_from_hf(model_b, progress_callback=progress_callback)
        
        # Step 2: Merge models
        job.status = "merging"
        job.current_step = "Merging layers..."
        job.progress_percent = 40
        db.commit()
        
        merged_path = merge_engine.merge_models(
            model_a=path_a,
            model_b=path_b,
            method=method,
            ratio=ratio,
            progress_callback=progress_callback
        )
        
        # Step 3: Quantize if needed
        if output_format.startswith("gguf"):
            job.status = "quantizing"
            job.current_step = f"Quantizing to {output_format}..."
            job.progress_percent = 70
            db.commit()
            
            bits = output_format.split("-")[1]
            quantized_path, file_size = quantizer.quantize_gguf(
                merged_path,
                bits=bits if bits != "f16" else "f16",
                progress_callback=progress_callback
            )
            final_path = quantized_path
        else:
            final_path = merged_path
            file_size = sum(f.stat().st_size for f in Path(final_path).rglob("*") if f.is_file())
        
        # Step 4: Calculate hash
        job.status = "verifying"
        job.current_step = "Verifying integrity..."
        job.progress_percent = 90
        db.commit()
        
        sha256_hash = hash_service.calculate_sha256(final_path)
        
        # Step 5: Complete
        job.status = "completed"
        job.current_step = "Done!"
        job.progress_percent = 100
        job.output_path = final_path
        job.file_size = file_size
        job.sha256_hash = sha256_hash
        job.completed_at = datetime.utcnow()
        db.commit()
        
        # Remove from active jobs
        if job_id in active_jobs:
            del active_jobs[job_id]
        
        logger.info(f"Merge job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Merge job {job_id} failed: {e}")
        
        # Update job with error
        job = db.query(MergeJob).filter(MergeJob.job_id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.current_step = f"Error: {str(e)}"
            db.commit()
        
        if job_id in active_jobs:
            del active_jobs[job_id]
        
        raise


@router.post("", response_model=MergeResponse, status_code=201)
async def create_merge_job(request: MergeRequest, db: Session = Depends(get_db)):
    """Create a new merge job."""
    
    # Generate job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Create database record
    job = MergeJob(
        job_id=job_id,
        model_a=request.model_a,
        model_b=request.model_b,
        method=request.method,
        ratio=request.ratio,
        output_format=request.output_format,
        output_name=request.output_name,
        status="pending",
        current_step="Initializing..."
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Estimate time based on model sizes (rough estimate)
    estimated_time = 300  # 5 minutes default
    
    # Start background task
    asyncio.create_task(run_merge_job(
        job_id=job_id,
        model_a=request.model_a,
        model_b=request.model_b,
        method=request.method,
        ratio=request.ratio,
        output_format=request.output_format,
        output_name=request.output_name,
        db=db
    ))
    
    return MergeResponse(
        job_id=job_id,
        status="pending",
        message=f"Merge job created. Merging {request.model_a} + {request.model_b}",
        estimated_time_seconds=estimated_time
    )


@router.get("/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Get status of a merge job."""
    
    job = db.query(MergeJob).filter(MergeJob.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Calculate ETA
    eta_seconds = None
    if job.status == "processing" and job.progress_percent > 0:
        elapsed = (datetime.utcnow() - job.created_at).total_seconds()
        if job.progress_percent < 100:
            eta_seconds = int((elapsed / job.progress_percent) * (100 - job.progress_percent))
    
    return JobStatus(
        job_id=job.job_id,
        status=job.status,
        progress_percent=job.progress_percent,
        current_step=job.current_step,
        eta_seconds=eta_seconds,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@router.get("/{job_id}/download")
async def download_merged_model(job_id: str, db: Session = Depends(get_db)):
    """Download the merged model file."""
    from fastapi.responses import FileResponse
    
    job = db.query(MergeJob).filter(MergeJob.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Status: {job.status}"
        )
    
    if not job.output_path:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    from pathlib import Path
    file_path = Path(job.output_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
        headers={
            "X-SHA256": job.sha256_hash or "",
            "X-File-Size": str(job.file_size or 0),
            "X-Model-Name": job.output_name,
            "Content-Disposition": f'attachment; filename="{file_path.name}"'
        }
    )


@router.post("/{job_id}/test", response_model=TestResponse)
async def test_merged_model(
    job_id: str,
    request: TestRequest,
    db: Session = Depends(get_db)
):
    """Test the merged model with a prompt."""
    
    job = db.query(MergeJob).filter(MergeJob.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    if not job.output_path:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    try:
        runner = TestRunner()
        runner.load_model(job.output_path)
        
        result = runner.chat(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        runner.unload()
        
        return TestResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.post("/{job_id}/deploy", response_model=DeployResponse)
async def deploy_model(
    job_id: str,
    request: DeployRequest,
    db: Session = Depends(get_db)
):
    """Deploy the merged model as an API endpoint."""
    import uuid
    from database import DeployedModel
    
    job = db.query(MergeJob).filter(MergeJob.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # Generate deployment
    deploy_id = f"deploy_{uuid.uuid4().hex[:8]}"
    api_key = f"ml_{uuid.uuid4().hex}"
    
    # In production, this would start a container/serverless function
    api_url = f"https://api.mergelab.intellectlabs.ai/v1/{deploy_id}"
    
    deployed = DeployedModel(
        deploy_id=deploy_id,
        job_id=job_id,
        model_path=job.output_path,
        api_key=api_key,
        api_url=api_url,
        expires_at=datetime.utcnow()
    )
    
    db.add(deployed)
    db.commit()
    
    return DeployResponse(
        deploy_id=deploy_id,
        api_url=api_url,
        api_key=api_key,
        expires_at=deployed.expires_at,
        status="active"
    )


@router.post("/{job_id}/push-hf", response_model=HFPushResponse)
async def push_to_huggingface(
    job_id: str,
    request: HFPushRequest,
    db: Session = Depends(get_db)
):
    """Push merged model to HuggingFace Hub."""
    
    job = db.query(MergeJob).filter(MergeJob.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    if not job.output_path:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    try:
        pusher = HFPusher(token=request.token)
        
        model_info = {
            "name": job.output_name,
            "model_a": job.model_a,
            "model_b": job.model_b,
            "method": job.method,
            "ratio": job.ratio,
            "format": job.output_format,
            "file_size_human": Quantizer().get_file_size_human(job.file_size or 0)
        }
        
        hf_url = pusher.push_to_hub(
            model_path=job.output_path,
            repo_id=request.repo_id,
            private=request.private,
            model_info=model_info
        )
        
        return HFPushResponse(
            success=True,
            hf_url=hf_url,
            message=f"Successfully pushed to {hf_url}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Push failed: {str(e)}")


from pathlib import Path
