"""Utility functions for image processing."""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Union
from src.config.settings import settings


def load_image(
    image_path: Union[str, Path],
    max_dimension: Optional[int] = None
) -> np.ndarray:
    """
    Load an image from file and optionally resize it.

    Args:
        image_path: Path to the image file
        max_dimension: Maximum dimension (width or height) for resizing.
                      If None, uses settings.max_image_dimension

    Returns:
        numpy.ndarray: Loaded image in BGR format

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be loaded
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Load image
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")

    # Resize if needed
    if max_dimension is None:
        max_dimension = settings.max_image_dimension

    height, width = image.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    return image


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Convert image to grayscale and apply preprocessing.

    Args:
        image: Input image in BGR format

    Returns:
        numpy.ndarray: Preprocessed grayscale image

    Raises:
        ValueError: If image is invalid
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image: empty or None")

    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Apply Gaussian blur to reduce noise
    kernel_size = settings.gaussian_blur_kernel
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

    return blurred


def detect_edges(image: np.ndarray) -> np.ndarray:
    """
    Detect edges using Canny edge detection.

    Args:
        image: Grayscale image

    Returns:
        numpy.ndarray: Edge-detected image

    Raises:
        ValueError: If image is invalid
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image: empty or None")

    # Ensure image is grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(
        image,
        settings.canny_threshold1,
        settings.canny_threshold2
    )

    return edges


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Order points in consistent order: top-left, top-right, bottom-right, bottom-left.

    Args:
        pts: Array of 4 points with shape (4, 2)

    Returns:
        numpy.ndarray: Ordered points with shape (4, 2)

    Raises:
        ValueError: If pts doesn't have exactly 4 points
    """
    if pts.shape[0] != 4:
        raise ValueError(f"Expected 4 points, got {pts.shape[0]}")

    # Reshape if needed
    pts = pts.reshape(4, 2)

    # Initialize ordered rectangle
    rect = np.zeros((4, 2), dtype="float32")

    # Sum and difference to find corners
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    # Top-left point has smallest sum
    rect[0] = pts[np.argmin(s)]

    # Bottom-right point has largest sum
    rect[2] = pts[np.argmax(s)]

    # Top-right point has smallest difference
    rect[1] = pts[np.argmin(diff)]

    # Bottom-left point has largest difference
    rect[3] = pts[np.argmax(diff)]

    return rect
