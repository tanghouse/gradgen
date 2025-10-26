from pathlib import Path
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.db.database import SessionLocal
from app.models import GenerationJob, GeneratedImage, JobStatus
from app.services.generation_service import generation_service


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
            # Generate portrait
            input_path = Path(image.input_image_path)
            board_path = Path(image.board_image_path)

            result_bytes = generation_service.generate_portrait(
                selfie_path=input_path,
                board_path=board_path,
                prompt_id=job.prompt_id or "P2"
            )

            # Save result
            results_dir = Path("results") / str(job.user_id)
            results_dir.mkdir(parents=True, exist_ok=True)

            output_path = results_dir / f"{job.id}_{image.id}.png"
            output_path.write_bytes(result_bytes)

            # Update image record
            image.output_image_path = str(output_path)
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

        results_dir = Path("results") / str(job.user_id)
        results_dir.mkdir(parents=True, exist_ok=True)

        for idx, image in enumerate(images):
            try:
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={'current': idx, 'total': len(images)}
                )

                # Generate portrait
                input_path = Path(image.input_image_path)
                board_path = Path(image.board_image_path)

                result_bytes = generation_service.generate_portrait(
                    selfie_path=input_path,
                    board_path=board_path,
                    prompt_id=job.prompt_id or "P2"
                )

                # Save result
                output_path = results_dir / f"{job.id}_{image.id}.png"
                output_path.write_bytes(result_bytes)

                # Update image record
                image.output_image_path = str(output_path)
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
