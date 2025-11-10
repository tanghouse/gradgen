from pathlib import Path
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.db.database import SessionLocal
from app.models import GenerationJob, GeneratedImage, JobStatus
from app.services.generation_service import generation_service
from app.services.storage_service import storage_service
from app.services.watermark_service import WatermarkService


@celery_app.task(bind=True)
def process_single_generation(self, job_id: int):
    """Process a single portrait generation job."""
    db = SessionLocal()
    try:
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        job.status = JobStatus.PROCESSING
        db.commit()

        # Get the image to process
        image = db.query(GeneratedImage).filter(GeneratedImage.job_id == job_id).first()
        if not image:
            job.status = JobStatus.FAILED
            job.error_message = "No image found for job"
            db.commit()
            return {"error": "No image found"}

        try:
            # Download input image from storage
            temp_dir = Path("/tmp/generation") / str(job.id)
            temp_dir.mkdir(parents=True, exist_ok=True)

            input_temp_path = temp_dir / f"input_{image.id}.jpg"
            storage_service.download_file(image.input_image_path, input_temp_path)

            # Board path is still local (in templates/ directory)
            board_path = Path(image.board_image_path)

            # Generate portrait
            result_bytes = generation_service.generate_portrait(
                selfie_path=input_temp_path,
                board_path=board_path,
                prompt_id=job.prompt_id or "P2"
            )

            # Save result to temp file
            output_temp_path = temp_dir / f"output_{job.id}_{image.id}.png"
            output_temp_path.write_bytes(result_bytes)

            # Upload result to storage
            output_object_key = f"results/{job.user_id}/{job.id}_{image.id}.png"
            storage_url = storage_service.upload_file(output_temp_path, output_object_key)

            # Clean up temp files
            input_temp_path.unlink(missing_ok=True)
            output_temp_path.unlink(missing_ok=True)

            # Update image record
            image.output_image_path = output_object_key
            image.success = True
            image.processed_at = datetime.utcnow()

            job.completed_images = 1
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()

        except Exception as e:
            image.success = False
            image.error_message = str(e)
            job.failed_images = 1
            job.status = JobStatus.FAILED
            job.error_message = str(e)

        db.commit()
        return {"status": "completed", "job_id": job_id}

    finally:
        db.close()


@celery_app.task(bind=True)
def process_batch_generation(self, job_id: int):
    """Process a batch portrait generation job."""
    db = SessionLocal()
    try:
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        job.status = JobStatus.PROCESSING
        db.commit()

        # Get all images to process
        images = db.query(GeneratedImage).filter(GeneratedImage.job_id == job_id).all()

        temp_dir = Path("/tmp/generation") / str(job.id)
        temp_dir.mkdir(parents=True, exist_ok=True)

        for idx, image in enumerate(images):
            try:
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={'current': idx, 'total': len(images)}
                )

                # Download input image from storage
                input_temp_path = temp_dir / f"input_{image.id}.jpg"
                storage_service.download_file(image.input_image_path, input_temp_path)

                # Board path is still local (in templates/ directory)
                board_path = Path(image.board_image_path)

                # Generate portrait
                result_bytes = generation_service.generate_portrait(
                    selfie_path=input_temp_path,
                    board_path=board_path,
                    prompt_id=job.prompt_id or "P2"
                )

                # Save result to temp file
                output_temp_path = temp_dir / f"output_{job.id}_{image.id}.png"
                output_temp_path.write_bytes(result_bytes)

                # Upload result to storage
                output_object_key = f"results/{job.user_id}/{job.id}_{image.id}.png"
                storage_url = storage_service.upload_file(output_temp_path, output_object_key)

                # Clean up temp files
                input_temp_path.unlink(missing_ok=True)
                output_temp_path.unlink(missing_ok=True)

                # Update image record
                image.output_image_path = output_object_key
                image.success = True
                image.processed_at = datetime.utcnow()

                job.completed_images += 1

            except Exception as e:
                image.success = False
                image.error_message = str(e)
                job.failed_images += 1

            db.commit()

        # Update job status
        if job.completed_images == job.total_images:
            job.status = JobStatus.COMPLETED
        elif job.completed_images > 0:
            job.status = JobStatus.COMPLETED  # Partial success
            job.error_message = f"{job.failed_images} images failed"
        else:
            job.status = JobStatus.FAILED
            job.error_message = "All images failed to generate"

        job.completed_at = datetime.utcnow()
        db.commit()

        return {"status": "completed", "job_id": job_id}

    finally:
        db.close()


@celery_app.task(bind=True)
def process_tier_generation(self, job_id: int):
    """
    Process tier-based generation (free or premium).
    Generates 5 photos with different prompts.
    Applies watermarks for free tier.
    """
    db = SessionLocal()
    try:
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        job.status = JobStatus.PROCESSING
        db.commit()

        # Get all images to process (one per prompt)
        images = db.query(GeneratedImage).filter(GeneratedImage.job_id == job_id).all()

        temp_dir = Path("/tmp/generation") / str(job.id)
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Download input image once (same for all prompts)
        if not images:
            job.status = JobStatus.FAILED
            job.error_message = "No images found for job"
            db.commit()
            return {"error": "No images found"}

        first_image = images[0]
        input_temp_path = temp_dir / f"input_{first_image.id}.jpg"
        storage_service.download_file(first_image.input_image_path, input_temp_path)

        # Board path is local
        board_path = Path(first_image.board_image_path)

        # Process each prompt
        for idx, image in enumerate(images):
            try:
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={'current': idx, 'total': len(images)}
                )

                # Generate portrait using custom prompt (unwatermarked version)
                unwatermarked_bytes = generation_service.generate_portrait(
                    selfie_path=input_temp_path,
                    board_path=board_path,
                    custom_prompt=image.prompt_text
                )

                # ALWAYS save unwatermarked version first
                unwatermarked_temp_path = temp_dir / f"unwatermarked_{job.id}_{image.id}.png"
                unwatermarked_temp_path.write_bytes(unwatermarked_bytes)

                unwatermarked_object_key = f"results/{job.user_id}/unwatermarked_{job.id}_{image.id}.png"
                storage_service.upload_file(unwatermarked_temp_path, unwatermarked_object_key)
                unwatermarked_temp_path.unlink(missing_ok=True)

                # For free tier, ALSO save watermarked version for display
                if job.is_watermarked:
                    watermarked_bytes = WatermarkService.add_watermark(
                        unwatermarked_bytes,
                        position="bottom_right"
                        # Uses default opacity (0.7) for better visibility
                    )

                    watermarked_temp_path = temp_dir / f"watermarked_{job.id}_{image.id}.png"
                    watermarked_temp_path.write_bytes(watermarked_bytes)

                    watermarked_object_key = f"results/{job.user_id}/watermarked_{job.id}_{image.id}.png"
                    storage_service.upload_file(watermarked_temp_path, watermarked_object_key)
                    watermarked_temp_path.unlink(missing_ok=True)

                    # For free tier: show watermarked version
                    image.output_image_path = watermarked_object_key
                else:
                    # For premium tier: show unwatermarked version
                    image.output_image_path = unwatermarked_object_key

                # Update image record with BOTH paths
                image.output_image_path_unwatermarked = unwatermarked_object_key  # Always saved
                image.success = True
                image.processed_at = datetime.utcnow()

                job.completed_images += 1

            except Exception as e:
                image.success = False
                image.error_message = str(e)
                job.failed_images += 1

            db.commit()

        # Clean up input file
        input_temp_path.unlink(missing_ok=True)

        # Update job status
        if job.completed_images == job.total_images:
            job.status = JobStatus.COMPLETED
        elif job.completed_images > 0:
            job.status = JobStatus.COMPLETED  # Partial success
            job.error_message = f"{job.failed_images} images failed"
        else:
            job.status = JobStatus.FAILED
            job.error_message = "All images failed to generate"

        job.completed_at = datetime.utcnow()
        db.commit()

        return {"status": "completed", "job_id": job_id}

    finally:
        db.close()


@celery_app.task(bind=True)
def retry_single_image(self, image_id: int):
    """
    Retry generation of a single failed image.
    Follows the same watermark/unwatermarked logic based on job tier.
    """
    db = SessionLocal()
    try:
        # Get the image
        image = db.query(GeneratedImage).filter(GeneratedImage.id == image_id).first()
        if not image:
            return {"error": "Image not found"}

        # Get the job to check tier/watermark settings
        job = db.query(GenerationJob).filter(GenerationJob.id == image.job_id).first()
        if not job:
            return {"error": "Job not found"}

        temp_dir = Path("/tmp/retry") / str(job.id)
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Download input image from storage
            input_temp_path = temp_dir / f"input_{image.id}.jpg"
            storage_service.download_file(image.input_image_path, input_temp_path)

            # Board path is local
            board_path = Path(image.board_image_path)

            # Generate unwatermarked portrait using the custom prompt
            unwatermarked_bytes = generation_service.generate_portrait(
                selfie_path=input_temp_path,
                board_path=board_path,
                custom_prompt=image.prompt_text
            )

            # ALWAYS save unwatermarked version first
            unwatermarked_temp_path = temp_dir / f"unwatermarked_{image.id}.png"
            unwatermarked_temp_path.write_bytes(unwatermarked_bytes)

            unwatermarked_object_key = f"results/{job.user_id}/unwatermarked_{job.id}_{image.id}.png"
            storage_service.upload_file(unwatermarked_temp_path, unwatermarked_object_key)
            unwatermarked_temp_path.unlink(missing_ok=True)

            # For free tier, ALSO save watermarked version for display
            if job.is_watermarked:
                watermarked_bytes = WatermarkService.add_watermark(
                    unwatermarked_bytes,
                    position="bottom_right"
                )

                watermarked_temp_path = temp_dir / f"watermarked_{image.id}.png"
                watermarked_temp_path.write_bytes(watermarked_bytes)

                watermarked_object_key = f"results/{job.user_id}/watermarked_{job.id}_{image.id}.png"
                storage_service.upload_file(watermarked_temp_path, watermarked_object_key)
                watermarked_temp_path.unlink(missing_ok=True)

                # For free tier: show watermarked version
                image.output_image_path = watermarked_object_key
            else:
                # For premium tier: show unwatermarked version
                image.output_image_path = unwatermarked_object_key

            # Update image record with BOTH paths
            image.output_image_path_unwatermarked = unwatermarked_object_key
            image.success = True
            image.error_message = None
            image.processed_at = datetime.now(timezone.utc)

            # Clean up input file
            input_temp_path.unlink(missing_ok=True)

            # Update job counters
            job.completed_images += 1

            # Update job status if needed
            if job.completed_images == job.total_images:
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now(timezone.utc)

        except Exception as e:
            image.success = False
            image.error_message = str(e)
            job.failed_images += 1

        db.commit()
        return {"status": "completed", "image_id": image_id}

    finally:
        db.close()


@celery_app.task(bind=True)
def regenerate_unwatermarked_photos(self, user_id: int):
    """
    Regenerate all watermarked photos without watermarks after premium upgrade.
    This is called after a user purchases premium tier.
    """
    db = SessionLocal()
    try:
        # Get all completed jobs for this user that were watermarked
        jobs = db.query(GenerationJob).filter(
            GenerationJob.user_id == user_id,
            GenerationJob.is_watermarked == True,
            GenerationJob.status == JobStatus.COMPLETED
        ).all()

        if not jobs:
            return {"status": "no_jobs", "message": "No watermarked photos to regenerate"}

        total_regenerated = 0
        temp_dir = Path("/tmp/regeneration") / str(user_id)
        temp_dir.mkdir(parents=True, exist_ok=True)

        for job in jobs:
            # Get all successful images from this job
            images = db.query(GeneratedImage).filter(
                GeneratedImage.job_id == job.id,
                GeneratedImage.success == True
            ).all()

            for image in images:
                try:
                    # Download input image from storage
                    input_temp_path = temp_dir / f"input_{image.id}.jpg"
                    storage_service.download_file(image.input_image_path, input_temp_path)

                    # Board path is still local
                    board_path = Path(image.board_image_path)

                    # Generate unwatermarked version using the same prompt
                    result_bytes = generation_service.generate_portrait(
                        selfie_path=input_temp_path,
                        board_path=board_path,
                        custom_prompt=image.prompt_text
                    )

                    # NO watermark this time!

                    # Save result to temp file
                    output_temp_path = temp_dir / f"unwatermarked_{image.id}.png"
                    output_temp_path.write_bytes(result_bytes)

                    # Upload unwatermarked version to storage (replace watermarked version)
                    storage_url = storage_service.upload_file(output_temp_path, image.output_image_path)

                    # Clean up temp files
                    input_temp_path.unlink(missing_ok=True)
                    output_temp_path.unlink(missing_ok=True)

                    total_regenerated += 1

                except Exception as e:
                    # Log error but continue with other images
                    print(f"Failed to regenerate image {image.id}: {e}")

        # Update all jobs to mark them as unwatermarked
        for job in jobs:
            job.is_watermarked = False

        db.commit()

        return {
            "status": "success",
            "user_id": user_id,
            "jobs_updated": len(jobs),
            "photos_regenerated": total_regenerated
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
