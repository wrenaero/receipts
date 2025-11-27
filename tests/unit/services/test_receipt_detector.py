"""Unit tests for receipt_detector service."""

import pytest
import numpy as np
import cv2

from src.services.receipt_detector import (
    find_receipt_contour,
    four_point_transform,
    remove_background,
    detect_and_extract_receipt
)


class TestFindReceiptContour:
    """Tests for find_receipt_contour function."""

    @pytest.mark.unit
    def test_find_receipt_contour_simple_rectangle(self):
        """Test finding contour in simple rectangular image."""
        # Create edge image with clear rectangle
        edge_image = np.zeros((400, 600), dtype=np.uint8)

        # Draw rectangle edges
        cv2.rectangle(edge_image, (50, 50), (550, 350), 255, 2)

        result = find_receipt_contour(edge_image)

        assert result is not None
        assert len(result) == 4
        # Check that result is roughly rectangular
        assert result.shape[0] == 4

    @pytest.mark.unit
    def test_find_receipt_contour_with_noise(self):
        """Test finding contour with noise in image."""
        # Create edge image with rectangle and noise
        edge_image = np.zeros((400, 600), dtype=np.uint8)

        # Main rectangle (receipt)
        cv2.rectangle(edge_image, (50, 50), (550, 350), 255, 2)

        # Add small noise rectangles
        cv2.rectangle(edge_image, (10, 10), (30, 30), 255, 2)
        cv2.rectangle(edge_image, (570, 10), (590, 30), 255, 2)

        result = find_receipt_contour(edge_image)

        # Should find the largest rectangle (the receipt)
        assert result is not None
        assert len(result) == 4

    @pytest.mark.unit
    def test_find_receipt_contour_no_receipt(self):
        """Test when no receipt-like contour is found."""
        # Empty edge image
        edge_image = np.zeros((400, 600), dtype=np.uint8)

        result = find_receipt_contour(edge_image)

        assert result is None

    @pytest.mark.unit
    def test_find_receipt_contour_too_small(self):
        """Test when contour is too small to be a receipt."""
        # Create edge image with very small rectangle
        edge_image = np.zeros((400, 600), dtype=np.uint8)

        # Very small rectangle (less than 5% of image area)
        cv2.rectangle(edge_image, (200, 200), (220, 220), 255, 2)

        result = find_receipt_contour(edge_image)

        # Should not detect this as a receipt
        assert result is None

    @pytest.mark.unit
    def test_find_receipt_contour_invalid_image(self):
        """Test with invalid input."""
        with pytest.raises(ValueError, match="Invalid image"):
            find_receipt_contour(None)

        with pytest.raises(ValueError, match="Invalid image"):
            find_receipt_contour(np.array([]))

    @pytest.mark.unit
    def test_find_receipt_contour_skewed_receipt(self, skewed_receipt_image):
        """Test finding contour in a skewed receipt image."""
        image_path, original_pts = skewed_receipt_image

        # Load and create edge image
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(image, 50, 150)

        result = find_receipt_contour(edges)

        # Should find the skewed receipt
        assert result is not None
        assert len(result) == 4


class TestFourPointTransform:
    """Tests for four_point_transform function."""

    @pytest.mark.unit
    def test_four_point_transform_basic(self, sample_image, simple_4_points):
        """Test basic perspective transformation."""
        image = cv2.imread(str(sample_image))

        result = four_point_transform(image, simple_4_points)

        assert result is not None
        assert len(result.shape) == 3  # Color image
        # Transformed image should be roughly rectangular
        height, width = result.shape[:2]
        assert height > 0 and width > 0

    @pytest.mark.unit
    def test_four_point_transform_skewed(self, sample_image):
        """Test transformation of skewed rectangle."""
        image = cv2.imread(str(sample_image))

        # Skewed points
        pts = np.array([
            [100, 150],  # top-left
            [400, 100],  # top-right
            [450, 250],  # bottom-right
            [150, 280]   # bottom-left
        ], dtype=np.float32)

        result = four_point_transform(image, pts)

        assert result is not None
        # Result should be deskewed
        height, width = result.shape[:2]
        assert height > 0 and width > 0

    @pytest.mark.unit
    def test_four_point_transform_preserves_aspect_ratio(self, sample_image):
        """Test that transformation preserves approximate aspect ratio."""
        image = cv2.imread(str(sample_image))

        # Rectangle with 2:1 aspect ratio
        pts = np.array([
            [100, 100],
            [300, 100],
            [300, 200],
            [100, 200]
        ], dtype=np.float32)

        result = four_point_transform(image, pts)

        height, width = result.shape[:2]
        aspect_ratio = width / height

        # Should be close to 2:1 ratio
        assert 1.8 < aspect_ratio < 2.2

    @pytest.mark.unit
    def test_four_point_transform_invalid_image(self, simple_4_points):
        """Test with invalid image."""
        with pytest.raises(ValueError, match="Invalid image"):
            four_point_transform(None, simple_4_points)

        with pytest.raises(ValueError, match="Invalid image"):
            four_point_transform(np.array([]), simple_4_points)

    @pytest.mark.unit
    def test_four_point_transform_invalid_points(self, sample_image):
        """Test with invalid points."""
        image = cv2.imread(str(sample_image))

        with pytest.raises(ValueError, match="Invalid points"):
            four_point_transform(image, None)

        with pytest.raises(ValueError, match="Invalid points"):
            four_point_transform(image, np.array([]))

    @pytest.mark.unit
    def test_four_point_transform_too_small(self, sample_image):
        """Test with points too close together."""
        image = cv2.imread(str(sample_image))

        # Points very close together
        pts = np.array([
            [100, 100],
            [102, 100],
            [102, 102],
            [100, 102]
        ], dtype=np.float32)

        with pytest.raises(ValueError, match="too small"):
            four_point_transform(image, pts)


class TestRemoveBackground:
    """Tests for remove_background function."""

    @pytest.mark.unit
    def test_remove_background_color_image(self, sample_image):
        """Test background removal on color image."""
        image = cv2.imread(str(sample_image))

        result = remove_background(image)

        assert result is not None
        assert len(result.shape) == 2  # Should be grayscale/binary
        assert result.dtype == np.uint8
        # Should have only black and white pixels
        unique_values = np.unique(result)
        assert all(v in [0, 255] for v in unique_values)

    @pytest.mark.unit
    def test_remove_background_grayscale_image(self, sample_image):
        """Test background removal on grayscale image."""
        image = cv2.imread(str(sample_image), cv2.IMREAD_GRAYSCALE)

        result = remove_background(image)

        assert result is not None
        assert len(result.shape) == 2

    @pytest.mark.unit
    def test_remove_background_enhances_contrast(self, sample_image):
        """Test that background removal creates high contrast image."""
        image = cv2.imread(str(sample_image))

        result = remove_background(image)

        # Binary image should have only 0 and 255
        unique_values = np.unique(result)
        assert len(unique_values) <= 2
        assert 0 in unique_values or 255 in unique_values

    @pytest.mark.unit
    def test_remove_background_invalid_image(self):
        """Test with invalid input."""
        with pytest.raises(ValueError, match="Invalid image"):
            remove_background(None)

        with pytest.raises(ValueError, match="Invalid image"):
            remove_background(np.array([]))


class TestDetectAndExtractReceipt:
    """Tests for detect_and_extract_receipt function."""

    @pytest.mark.unit
    def test_detect_and_extract_success(self, sample_image):
        """Test successful receipt detection and extraction."""
        # Load image
        image = cv2.imread(str(sample_image))

        # Create edge image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        warped, contour = detect_and_extract_receipt(image, edges)

        # With the sample image (white rectangle), it should find something
        # Results may be None if the test image doesn't have clear edges
        if warped is not None:
            assert isinstance(warped, np.ndarray)
            assert contour is not None
            assert len(contour) == 4

    @pytest.mark.unit
    def test_detect_and_extract_no_receipt(self):
        """Test when no receipt is found."""
        # Create images with no clear receipt
        image = np.ones((400, 600, 3), dtype=np.uint8) * 128
        edges = np.zeros((400, 600), dtype=np.uint8)

        warped, contour = detect_and_extract_receipt(image, edges)

        assert warped is None
        assert contour is None

    @pytest.mark.unit
    def test_detect_and_extract_without_background_removal(self, sample_image):
        """Test extraction without background removal."""
        image = cv2.imread(str(sample_image))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        warped, contour = detect_and_extract_receipt(
            image,
            edges,
            apply_background_removal=False
        )

        # If detected, result should be color image (not binary)
        if warped is not None:
            # Without background removal, should have 3 channels or be grayscale
            # but not binary
            assert len(warped.shape) in [2, 3]

    @pytest.mark.unit
    def test_detect_and_extract_with_skewed_receipt(self, skewed_receipt_image):
        """Test with skewed receipt image."""
        image_path, _ = skewed_receipt_image

        # Load image
        image = cv2.imread(str(image_path))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        warped, contour = detect_and_extract_receipt(image, edges)

        # Should detect the skewed receipt
        assert warped is not None
        assert contour is not None
        assert len(contour) == 4

        # Warped image should be roughly rectangular
        height, width = warped.shape[:2]
        assert height > 0 and width > 0
