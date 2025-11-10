from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.generation_job import JobStatus


class GenerationRequest(BaseModel):
    university: str
    degree_level: str
    prompt_id: str = "P2"


class BatchGenerationRequest(BaseModel):
    university: str
    degree_level: str
    prompt_id: str = "P2"


class GeneratedImageResponse(BaseModel):
    id: int
    original_filename: str
    output_image_path: Optional[str]
    success: Optional[bool]  # None = processing, True = success, False = failed
    error_message: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GenerationJobResponse(BaseModel):
    id: int
    job_type: str
    status: JobStatus
    university: Optional[str]
    degree_level: Optional[str]
    prompt_id: Optional[str]
    total_images: int
    completed_images: int
    failed_images: int
    is_watermarked: bool = False
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    generated_images: List[GeneratedImageResponse] = []

    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    job_id: int
    status: JobStatus
    progress: float  # 0.0 to 1.0
    completed_images: int
    total_images: int
    message: Optional[str]
