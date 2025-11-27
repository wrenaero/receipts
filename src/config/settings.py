"""Application configuration settings."""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Receipt Scanner API"
    debug: bool = False

    # Image Processing
    max_image_dimension: int = 1500
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = ["jpg", "jpeg", "png"]

    # Edge Detection
    canny_threshold1: int = 75
    canny_threshold2: int = 200
    gaussian_blur_kernel: int = 5

    # OCR
    ocr_language: str = "en"
    ocr_use_angle_cls: bool = True

    # API
    upload_dir: str = "uploads"
    processed_dir: str = "processed"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()
