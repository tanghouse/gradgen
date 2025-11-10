from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("generation_jobs.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    input_image_path = Column(String, nullable=False)
    output_image_path = Column(String)  # Watermarked version (for free tier display)
    output_image_path_unwatermarked = Column(String)  # Non-watermarked version (for premium users)
    board_image_path = Column(String)
    prompt_text = Column(Text)
    success = Column(Boolean, nullable=True, default=None)  # None = processing, True = success, False = failed
    error_message = Column(Text)
    generation_metadata = Column(Text)  # JSON string with additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relationships
    job = relationship("GenerationJob", back_populates="generated_images")
