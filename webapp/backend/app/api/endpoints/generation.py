from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import uuid
import shutil
from typing import List

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models import User, GenerationJob, GeneratedImage, CreditTransaction, TransactionType, JobStatus
from app.schemas.generation import (
    GenerationRequest,
    BatchGenerationRequest,
    GenerationJobResponse,
    JobStatusResponse
)
from app.services.generation_service import generation_service
from app.tasks.generation_tasks import process_single_generation, process_batch_generation
from app.core.config import settings

router = APIRouter()


@router.get("/universities")
async def list_universities():
    """List all available universities and degree levels."""
    universities = generation_service.list_available_universities()
    return {"universities": universities}


@router.post("/single", response_model=GenerationJobResponse)
async def create_single_generation(
    file: UploadFile = File(...),
    university: str = Form(...),
    degree_level: str = Form(...),
    prompt_id: str = Form("P2"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a single portrait generation job.
    Requires 1 credit.
    """
    # Check credits
    if current_user.credits < settings.CREDITS_PER_PORTRAIT:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {settings.CREDITS_PER_PORTRAIT}, Available: {current_user.credits}"
        )

    # Check if board exists
    board_path = generation_service.get_board_path(university, degree_level)
    if not board_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design board not found for {university} - {degree_level}"
        )

    # Save uploaded file
    upload_dir = Path("uploads") / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create job
    job = GenerationJob(
        user_id=current_user.id,
        job_type="single",
        university=university,
        degree_level=degree_level,
        prompt_id=prompt_id,
        total_images=1,
        status=JobStatus.PENDING
    )
    db.add(job)
    db.flush()

    # Create image entry
    generated_image = GeneratedImage(
        job_id=job.id,
        original_filename=file.filename,
        input_image_path=str(file_path),
        board_image_path=str(board_path),
        prompt_text=generation_service.prompts.get(prompt_id, "")
    )
    db.add(generated_image)

    # Deduct credits
    current_user.credits -= settings.CREDITS_PER_PORTRAIT

    # Record transaction
    transaction = CreditTransaction(
        user_id=current_user.id,
        amount=-settings.CREDITS_PER_PORTRAIT,
        transaction_type=TransactionType.USAGE,
        description=f"Single portrait generation - {university} {degree_level}",
        reference_id=str(job.id)
    )
    db.add(transaction)

    db.commit()
    db.refresh(job)

    # Queue background task
    task = process_single_generation.delay(job.id)
    job.celery_task_id = task.id
    db.commit()

    return job


@router.post("/batch", response_model=GenerationJobResponse)
async def create_batch_generation(
    files: List[UploadFile] = File(...),
    university: str = Form(...),
    degree_level: str = Form(...),
    prompt_id: str = Form("P2"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a batch portrait generation job.
    Requires 1 credit per image.
    """
    num_images = len(files)
    required_credits = num_images * settings.CREDITS_PER_PORTRAIT

    # Check credits
    if current_user.credits < required_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {required_credits}, Available: {current_user.credits}"
        )

    # Check if board exists
    board_path = generation_service.get_board_path(university, degree_level)
    if not board_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design board not found for {university} - {degree_level}"
        )

    # Create job
    job = GenerationJob(
        user_id=current_user.id,
        job_type="batch",
        university=university,
        degree_level=degree_level,
        prompt_id=prompt_id,
        total_images=num_images,
        status=JobStatus.PENDING
    )
    db.add(job)
    db.flush()

    # Save uploaded files and create image entries
    upload_dir = Path("uploads") / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / unique_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        generated_image = GeneratedImage(
            job_id=job.id,
            original_filename=file.filename,
            input_image_path=str(file_path),
            board_image_path=str(board_path),
            prompt_text=generation_service.prompts.get(prompt_id, "")
        )
        db.add(generated_image)

    # Deduct credits
    current_user.credits -= required_credits

    # Record transaction
    transaction = CreditTransaction(
        user_id=current_user.id,
        amount=-required_credits,
        transaction_type=TransactionType.USAGE,
        description=f"Batch generation ({num_images} images) - {university} {degree_level}",
        reference_id=str(job.id)
    )
    db.add(transaction)

    db.commit()
    db.refresh(job)

    # Queue background task
    task = process_batch_generation.delay(job.id)
    job.celery_task_id = task.id
    db.commit()

    return job


@router.get("/jobs", response_model=List[GenerationJobResponse])
async def list_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """List user's generation jobs."""
    jobs = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id
    ).order_by(GenerationJob.created_at.desc()).limit(limit).all()

    return jobs


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get job details."""
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get job status (for polling)."""
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    progress = 0.0
    if job.total_images > 0:
        progress = job.completed_images / job.total_images

    message = None
    if job.status == JobStatus.FAILED:
        message = job.error_message

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=progress,
        completed_images=job.completed_images,
        total_images=job.total_images,
        message=message
    )


@router.get("/results/{image_id}")
async def download_result(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download generated image."""
    image = db.query(GeneratedImage).join(GenerationJob).filter(
        GeneratedImage.id == image_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if not image.output_image_path or not Path(image.output_image_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated image file not found"
        )

    return FileResponse(
        path=image.output_image_path,
        media_type="image/png",
        filename=f"gradgen_{image.original_filename}"
    )


@router.get("/inputs/{image_id}")
async def get_input_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the original uploaded image."""
    image = db.query(GeneratedImage).join(GenerationJob).filter(
        GeneratedImage.id == image_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if not image.input_image_path or not Path(image.input_image_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Input image file not found"
        )

    return FileResponse(
        path=image.input_image_path,
        media_type="image/jpeg"
    )
