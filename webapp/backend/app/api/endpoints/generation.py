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
from app.services.storage_service import storage_service
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
    # DEPRECATED: Credit system removed. Use /generate-tier instead.
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint is deprecated. Please use /generate-tier for tier-based generation."
    )

    # Check if board exists
    board_path = generation_service.get_board_path(university, degree_level)
    if not board_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design board not found for {university} - {degree_level}"
        )

    # Save uploaded file
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    # Save to temporary location first
    temp_dir = Path("/tmp/uploads") / str(current_user.id)
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = temp_dir / unique_filename

    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload to storage (R2 or local)
    object_key = f"uploads/{current_user.id}/{unique_filename}"
    storage_url = storage_service.upload_file(temp_file_path, object_key)

    # Clean up temp file
    temp_file_path.unlink(missing_ok=True)

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
        input_image_path=object_key,  # Store R2 object key, not local path
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
    # DEPRECATED: Credit system removed. Use /generate-tier instead.
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint is deprecated. Please use /generate-tier for tier-based generation."
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
    temp_dir = Path("/tmp/uploads") / str(current_user.id)
    temp_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        temp_file_path = temp_dir / unique_filename

        # Save to temporary location
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Upload to storage (R2 or local)
        object_key = f"uploads/{current_user.id}/{unique_filename}"
        storage_url = storage_service.upload_file(temp_file_path, object_key)

        # Clean up temp file
        temp_file_path.unlink(missing_ok=True)

        generated_image = GeneratedImage(
            job_id=job.id,
            original_filename=file.filename,
            input_image_path=object_key,  # Store R2 object key, not local path
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
    """
    Download generated image.

    Returns the appropriate version based on user's premium status:
    - Premium users: Always get unwatermarked version
    - Free tier users: Get watermarked version (for images generated during free tier)
    """
    image = db.query(GeneratedImage).join(GenerationJob).filter(
        GeneratedImage.id == image_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Determine which version to return
    object_key = None

    if current_user.has_purchased_premium:
        # Premium users ALWAYS get unwatermarked version
        # (even for photos generated during free tier)
        if image.output_image_path_unwatermarked:
            object_key = image.output_image_path_unwatermarked
        elif image.output_image_path:
            # Fallback for old images without unwatermarked version
            object_key = image.output_image_path
    else:
        # Free tier users get watermarked version
        if image.output_image_path:
            object_key = image.output_image_path
        else:
            # Shouldn't happen, but fallback to unwatermarked if that's all we have
            object_key = image.output_image_path_unwatermarked

    if not object_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated image not ready"
        )

    # Download from storage to temp file
    temp_file = Path("/tmp/downloads") / f"result_{image_id}.png"
    temp_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        storage_service.download_file(object_key, temp_file)

        return FileResponse(
            path=str(temp_file),
            media_type="image/png",
            filename=f"gradgen_{image.original_filename}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download image: {str(e)}"
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

    if not image.input_image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Input image not found"
        )

    # Download from storage to temp file
    temp_file = Path("/tmp/downloads") / f"input_{image_id}.jpg"
    temp_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        storage_service.download_file(image.input_image_path, temp_file)

        return FileResponse(
            path=str(temp_file),
            media_type="image/jpeg"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download image: {str(e)}"
        )


@router.post("/generate-tier", response_model=GenerationJobResponse)
async def generate_with_tier(
    file: UploadFile = File(...),
    university: str = Form(...),
    degree_level: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate graduation photos based on user's tier (free or premium).

    Free tier:
    - 5 prompts, 5 watermarked photos
    - Can only be used once per user
    - Sets has_used_free_tier = True

    Premium tier:
    - 5 random prompts, 5 unwatermarked photos
    - Requires has_purchased_premium = True
    - Can be used 2 times (2 generation opportunities)

    Returns job ID to poll for status.
    """
    # Determine tier
    tier = None
    if not current_user.has_used_free_tier:
        tier = "free"
    elif current_user.has_purchased_premium:
        # Check if user has premium generations left
        if current_user.premium_generations_used >= 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have used all your premium generation opportunities (2/2). Thank you for using GradGen!"
            )
        tier = "premium"
    else:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Free tier already used. Please purchase premium tier to continue."
        )

    # Check if board exists
    board_path = generation_service.get_board_path(university, degree_level)
    if not board_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design board not found for {university} - {degree_level}"
        )

    # Save uploaded file
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    temp_dir = Path("/tmp/uploads") / str(current_user.id)
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = temp_dir / unique_filename

    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload to storage
    object_key = f"uploads/{current_user.id}/{unique_filename}"
    storage_url = storage_service.upload_file(temp_file_path, object_key)

    # Clean up temp file
    temp_file_path.unlink(missing_ok=True)

    # Get prompts for tier
    prompts = generation_service.get_prompts_for_tier(tier, university, degree_level)
    num_prompts = len(prompts)

    # Create job
    job = GenerationJob(
        user_id=current_user.id,
        job_type=f"{tier}_tier",
        university=university,
        degree_level=degree_level,
        tier=tier,
        is_watermarked=(tier == "free"),
        total_images=num_prompts,
        status=JobStatus.PENDING,
        prompts_used=",".join(prompts.keys())  # Store comma-separated prompt IDs
    )
    db.add(job)
    db.flush()

    # Create image entries for each prompt
    for prompt_id, prompt_data in prompts.items():
        generated_image = GeneratedImage(
            job_id=job.id,
            original_filename=file.filename,
            input_image_path=object_key,
            board_image_path=str(board_path),
            prompt_text=prompt_data["prompt"]
        )
        db.add(generated_image)

    # Mark tier as used (before committing, in case of failure)
    if tier == "free":
        current_user.has_used_free_tier = True
    elif tier == "premium":
        current_user.premium_generations_used += 1

    db.commit()
    db.refresh(job)

    # Queue background task
    from app.tasks.generation_tasks import process_tier_generation
    task = process_tier_generation.delay(job.id)
    job.celery_task_id = task.id
    db.commit()

    return job


@router.get("/tier-status")
async def get_tier_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's current tier status

    Returns:
    - tier: "free", "premium", "premium_exhausted", or "needs_payment"
    - has_used_free_tier: Boolean
    - has_purchased_premium: Boolean
    - premium_generations_used: Integer (0-2)
    - premium_generations_remaining: Integer (0-2)
    - can_generate: Boolean
    """
    premium_generations_used = current_user.premium_generations_used if current_user.premium_generations_used else 0
    premium_generations_remaining = max(0, 2 - premium_generations_used)

    if not current_user.has_used_free_tier:
        tier = "free"
        can_generate = True
    elif current_user.has_purchased_premium and premium_generations_remaining > 0:
        tier = "premium"
        can_generate = True
    elif current_user.has_purchased_premium and premium_generations_remaining == 0:
        tier = "premium_exhausted"
        can_generate = False
    else:
        tier = "needs_payment"
        can_generate = False

    return {
        "tier": tier,
        "has_used_free_tier": current_user.has_used_free_tier,
        "has_purchased_premium": current_user.has_purchased_premium,
        "premium_generations_used": premium_generations_used,
        "premium_generations_remaining": premium_generations_remaining,
        "can_generate": can_generate,
        "message": "Free tier available (5 watermarked photos)" if tier == "free" else
                   f"Premium tier active ({premium_generations_remaining} generation{'s' if premium_generations_remaining != 1 else ''} remaining)" if tier == "premium" else
                   "All premium generations used (2/2)" if tier == "premium_exhausted" else
                   "Please purchase premium tier to continue"
    }


@router.post("/retry/{image_id}")
async def retry_image_generation(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retry a failed image generation.
    Clears the error and re-queues the image for processing.
    """
    # Get the image and verify ownership
    image = db.query(GeneratedImage).join(GenerationJob).filter(
        GeneratedImage.id == image_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Get the job
    job = db.query(GenerationJob).filter(GenerationJob.id == image.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Reset image status
    image.success = None  # Mark as pending
    image.error_message = None
    image.output_image_path = None
    image.output_image_path_unwatermarked = None
    image.processed_at = None

    # Update job counters
    if job.failed_images > 0:
        job.failed_images -= 1

    # If job was failed or completed, set back to processing
    if job.status in [JobStatus.FAILED, JobStatus.COMPLETED]:
        job.status = JobStatus.PROCESSING

    db.commit()

    # Re-queue the single image generation task
    from app.tasks.generation_tasks import retry_single_image
    task = retry_single_image.delay(image.id)

    return {"status": "success", "message": "Image generation retry queued", "task_id": task.id}


@router.post("/admin/run-migration")
async def run_migration(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Run database migration to add unwatermarked column.
    Only accessible to superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can run migrations"
        )

    from sqlalchemy import text

    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='generated_images'
            AND column_name='output_image_path_unwatermarked'
        """))

        if result.fetchone():
            return {"status": "success", "message": "Column 'output_image_path_unwatermarked' already exists"}

        # Add the new column
        db.execute(text("""
            ALTER TABLE generated_images
            ADD COLUMN output_image_path_unwatermarked VARCHAR
        """))
        db.commit()

        return {"status": "success", "message": "Successfully added column 'output_image_path_unwatermarked'"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )
