from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_type = Column(String, nullable=False)  # "single" or "batch"
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    university = Column(String)
    degree_level = Column(String)
    prompt_id = Column(String)
    total_images = Column(Integer, default=1)
    completed_images = Column(Integer, default=0)
    failed_images = Column(Integer, default=0)
    error_message = Column(Text)
    celery_task_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="generation_jobs")
    generated_images = relationship("GeneratedImage", back_populates="job", cascade="all, delete-orphan")
