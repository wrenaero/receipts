"""Pytest configuration and fixtures."""

import pytest
import numpy as np
import cv2
from pathlib import Path


@pytest.fixture
def test_image_dir(tmp_path):
    """Create temporary directory for test images."""
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    return img_dir


@pytest.fixture
def sample_image(test_image_dir):
    """Create a sample test image (white rectangle on black background)."""
    # Create 500x300 black image
    image = np.zeros((300, 500, 3), dtype=np.uint8)

    # Draw white rectangle (simulating a receipt)
    cv2.rectangle(image, (50, 50), (450, 250), (255, 255, 255), -1)

    # Add some text-like noise
    for i in range(10):
        x = np.random.randint(60, 440)
        y = np.random.randint(60, 240)
        cv2.putText(image, "TEXT", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # Save image
    image_path = test_image_dir / "sample.jpg"
    cv2.imwrite(str(image_path), image)

    return image_path


@pytest.fixture
def large_image(test_image_dir):
    """Create a large test image."""
    # Create 2000x2000 image
    image = np.ones((2000, 2000, 3), dtype=np.uint8) * 128

    # Save image
    image_path = test_image_dir / "large.jpg"
    cv2.imwrite(str(image_path), image)

    return image_path


@pytest.fixture
def skewed_receipt_image(test_image_dir):
    """Create a skewed receipt-like image."""
    # Create base image
    image = np.zeros((600, 800, 3), dtype=np.uint8)

    # Define receipt corners (skewed)
    pts = np.array([
        [100, 150],  # top-left
        [600, 100],  # top-right
        [650, 500],  # bottom-right
        [150, 550]   # bottom-left
    ], dtype=np.int32)

    # Draw white polygon
    cv2.fillPoly(image, [pts], (255, 255, 255))

    # Add some lines to simulate text
    for i in range(15):
        y = 150 + i * 25
        cv2.line(image, (120, y), (600, y), (0, 0, 0), 2)

    # Save image
    image_path = test_image_dir / "skewed.jpg"
    cv2.imwrite(str(image_path), image)

    return image_path, pts


@pytest.fixture
def simple_4_points():
    """Return simple 4-point array for testing."""
    return np.array([
        [100, 100],  # top-left
        [300, 100],  # top-right
        [300, 400],  # bottom-right
        [100, 400]   # bottom-left
    ], dtype=np.float32)


@pytest.fixture
def scrambled_4_points():
    """Return scrambled 4-point array (to test ordering)."""
    return np.array([
        [300, 400],  # bottom-right
        [100, 100],  # top-left
        [300, 100],  # top-right
        [100, 400]   # bottom-left
    ], dtype=np.float32)
