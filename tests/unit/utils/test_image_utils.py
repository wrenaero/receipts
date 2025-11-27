"""Unit tests for image_utils module."""

import pytest
import numpy as np
import cv2
from pathlib import Path

from src.utils.image_utils import (
    load_image,
    preprocess_image,
    detect_edges,
    order_points
)


class TestLoadImage:
    """Tests for load_image function."""

    @pytest.mark.unit
    def test_load_image_success(self, sample_image):
        """Test loading a valid image."""
        result = load_image(sample_image)

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 3  # Color image (H, W, C)
        assert result.shape[2] == 3    # BGR format

    @pytest.mark.unit
    def test_load_image_with_path_object(self, sample_image):
        """Test loading image with Path object."""
        result = load_image(Path(sample_image))

        assert result is not None
        assert isinstance(result, np.ndarray)

    @pytest.mark.unit
    def test_load_image_file_not_found(self):
        """Test loading non-existent image."""
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            load_image("/nonexistent/path/image.jpg")

    @pytest.mark.unit
    def test_load_image_invalid_file(self, tmp_path):
        """Test loading invalid image file."""
        # Create a text file with .jpg extension
        invalid_file = tmp_path / "invalid.jpg"
        invalid_file.write_text("not an image")

        with pytest.raises(ValueError, match="Failed to load image"):
            load_image(invalid_file)

    @pytest.mark.unit
    def test_load_image_resize_large_image(self, large_image):
        """Test that large images are resized."""
        result = load_image(large_image, max_dimension=500)

        height, width = result.shape[:2]
        assert max(height, width) == 500
        assert height == width == 500  # Square image should remain square

    @pytest.mark.unit
    def test_load_image_no_resize_small_image(self, sample_image):
        """Test that small images are not resized unnecessarily."""
        result = load_image(sample_image, max_dimension=1000)

        # Original is 500x300, should not be resized
        height, width = result.shape[:2]
        assert height == 300
        assert width == 500


class TestPreprocessImage:
    """Tests for preprocess_image function."""

    @pytest.mark.unit
    def test_preprocess_color_image(self, sample_image):
        """Test preprocessing a color image."""
        image = cv2.imread(str(sample_image))
        result = preprocess_image(image)

        assert result is not None
        assert len(result.shape) == 2  # Grayscale
        assert result.dtype == np.uint8

    @pytest.mark.unit
    def test_preprocess_grayscale_image(self, sample_image):
        """Test preprocessing an already grayscale image."""
        image = cv2.imread(str(sample_image))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        result = preprocess_image(gray)

        assert result is not None
        assert len(result.shape) == 2  # Still grayscale
        assert result.dtype == np.uint8

    @pytest.mark.unit
    def test_preprocess_applies_blur(self, sample_image):
        """Test that preprocessing applies Gaussian blur."""
        image = cv2.imread(str(sample_image))

        # Create a noisy image
        noisy = image.copy()
        noise = np.random.randint(0, 50, image.shape, dtype=np.uint8)
        noisy = cv2.add(noisy, noise)

        result = preprocess_image(noisy)

        # Blurred image should have lower standard deviation than original
        gray_noisy = cv2.cvtColor(noisy, cv2.COLOR_BGR2GRAY)
        assert np.std(result) <= np.std(gray_noisy)

    @pytest.mark.unit
    def test_preprocess_invalid_image(self):
        """Test preprocessing with invalid input."""
        with pytest.raises(ValueError, match="Invalid image"):
            preprocess_image(None)

        with pytest.raises(ValueError, match="Invalid image"):
            preprocess_image(np.array([]))


class TestDetectEdges:
    """Tests for detect_edges function."""

    @pytest.mark.unit
    def test_detect_edges_grayscale(self, sample_image):
        """Test edge detection on grayscale image."""
        image = cv2.imread(str(sample_image), cv2.IMREAD_GRAYSCALE)
        result = detect_edges(image)

        assert result is not None
        assert len(result.shape) == 2  # Binary edge image
        assert result.dtype == np.uint8
        assert np.max(result) <= 255
        assert np.min(result) >= 0

    @pytest.mark.unit
    def test_detect_edges_color_image(self, sample_image):
        """Test edge detection converts color to grayscale."""
        image = cv2.imread(str(sample_image))
        result = detect_edges(image)

        assert result is not None
        assert len(result.shape) == 2  # Should be grayscale

    @pytest.mark.unit
    def test_detect_edges_finds_edges(self, sample_image):
        """Test that edges are actually detected."""
        image = cv2.imread(str(sample_image), cv2.IMREAD_GRAYSCALE)
        result = detect_edges(image)

        # Should have some white pixels (edges detected)
        edge_pixels = np.count_nonzero(result == 255)
        assert edge_pixels > 0

    @pytest.mark.unit
    def test_detect_edges_invalid_image(self):
        """Test edge detection with invalid input."""
        with pytest.raises(ValueError, match="Invalid image"):
            detect_edges(None)

        with pytest.raises(ValueError, match="Invalid image"):
            detect_edges(np.array([]))


class TestOrderPoints:
    """Tests for order_points function."""

    @pytest.mark.unit
    def test_order_points_already_ordered(self, simple_4_points):
        """Test ordering points that are already in correct order."""
        result = order_points(simple_4_points)

        assert result.shape == (4, 2)
        assert result.dtype == np.float32

        # Check order: TL, TR, BR, BL
        np.testing.assert_array_almost_equal(result[0], [100, 100])  # TL
        np.testing.assert_array_almost_equal(result[1], [300, 100])  # TR
        np.testing.assert_array_almost_equal(result[2], [300, 400])  # BR
        np.testing.assert_array_almost_equal(result[3], [100, 400])  # BL

    @pytest.mark.unit
    def test_order_points_scrambled(self, scrambled_4_points):
        """Test ordering scrambled points."""
        result = order_points(scrambled_4_points)

        assert result.shape == (4, 2)

        # Check order: TL, TR, BR, BL
        np.testing.assert_array_almost_equal(result[0], [100, 100])  # TL
        np.testing.assert_array_almost_equal(result[1], [300, 100])  # TR
        np.testing.assert_array_almost_equal(result[2], [300, 400])  # BR
        np.testing.assert_array_almost_equal(result[3], [100, 400])  # BL

    @pytest.mark.unit
    def test_order_points_with_reshape(self):
        """Test ordering points with different input shape."""
        # Points in shape (4, 1, 2) - common from cv2.findContours
        pts = np.array([
            [[300, 400]],  # BR
            [[100, 100]],  # TL
            [[300, 100]],  # TR
            [[100, 400]]   # BL
        ], dtype=np.float32)

        result = order_points(pts)

        assert result.shape == (4, 2)
        np.testing.assert_array_almost_equal(result[0], [100, 100])  # TL

    @pytest.mark.unit
    def test_order_points_invalid_count(self):
        """Test with wrong number of points."""
        with pytest.raises(ValueError, match="Expected 4 points"):
            order_points(np.array([[0, 0], [1, 1]]))  # Only 2 points

        with pytest.raises(ValueError, match="Expected 4 points"):
            order_points(np.array([[0, 0]] * 5))  # 5 points

    @pytest.mark.unit
    def test_order_points_skewed_rectangle(self):
        """Test ordering points of a skewed rectangle."""
        # Skewed receipt-like corners
        pts = np.array([
            [150, 550],  # BL
            [650, 500],  # BR
            [100, 150],  # TL
            [600, 100]   # TR
        ], dtype=np.float32)

        result = order_points(pts)

        # Top-left should have smallest sum
        assert result[0][0] < result[2][0]  # TL.x < BR.x
        assert result[0][1] < result[2][1]  # TL.y < BR.y

        # Top-right should be in top half
        assert result[1][1] < (result[0][1] + result[2][1]) / 2
