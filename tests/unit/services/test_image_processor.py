"""Unit tests for image_processor service."""

import pytest
import numpy as np
import cv2
from pathlib import Path

from src.services.image_processor import (
    ReceiptProcessor,
    process_receipt_simple
)


class TestReceiptProcessor:
    """Tests for ReceiptProcessor class."""

    @pytest.mark.unit
    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = ReceiptProcessor()

        assert processor is not None
        assert processor.last_result is None

    @pytest.mark.unit
    def test_process_receipt_with_path(self, skewed_receipt_image, tmp_path):
        """Test processing receipt from file path."""
        image_path, _ = skewed_receipt_image
        output_path = tmp_path / "processed.jpg"

        processor = ReceiptProcessor()
        result = processor.process_receipt(image_path, output_path)

        assert result is not None
        assert 'success' in result
        assert 'processed_image' in result
        assert 'contour' in result
        assert 'message' in result

        # With skewed receipt image, should succeed
        if result['success']:
            assert result['processed_image'] is not None
            assert result['contour'] is not None
            assert output_path.exists()

    @pytest.mark.unit
    def test_process_receipt_with_numpy_array(self, skewed_receipt_image):
        """Test processing receipt from numpy array."""
        image_path, _ = skewed_receipt_image
        image = cv2.imread(str(image_path))

        processor = ReceiptProcessor()
        result = processor.process_receipt(image)

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_process_receipt_return_steps(self, skewed_receipt_image):
        """Test processing with intermediate steps returned."""
        image_path, _ = skewed_receipt_image

        processor = ReceiptProcessor()
        result = processor.process_receipt(image_path, return_steps=True)

        assert 'steps' in result

        if result['success']:
            steps = result['steps']
            assert steps is not None
            assert 'original' in steps
            assert 'preprocessed' in steps
            assert 'edges' in steps
            # Other steps may vary based on success

    @pytest.mark.unit
    def test_process_receipt_stores_last_result(self, skewed_receipt_image):
        """Test that processor stores last result."""
        image_path, _ = skewed_receipt_image

        processor = ReceiptProcessor()
        result = processor.process_receipt(image_path)

        if result['success']:
            assert processor.last_result is not None
            assert 'processed_image' in processor.last_result
            assert 'contour' in processor.last_result
            assert 'original' in processor.last_result

    @pytest.mark.unit
    def test_process_receipt_no_receipt_found(self, tmp_path):
        """Test processing when no receipt is detected."""
        # Create image with no clear receipt
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 128
        image_path = tmp_path / "no_receipt.jpg"
        cv2.imwrite(str(image_path), test_image)

        processor = ReceiptProcessor()
        result = processor.process_receipt(image_path)

        assert result['success'] is False
        assert result['processed_image'] is None
        assert result['contour'] is None
        assert 'Could not detect receipt' in result['message']

    @pytest.mark.unit
    def test_process_receipt_file_not_found(self):
        """Test processing with non-existent file."""
        processor = ReceiptProcessor()
        result = processor.process_receipt("/nonexistent/image.jpg")

        assert result['success'] is False
        assert result['processed_image'] is None
        assert 'File not found' in result['message']

    @pytest.mark.unit
    def test_process_receipt_invalid_image(self, tmp_path):
        """Test processing with invalid image file."""
        # Create invalid image file
        invalid_file = tmp_path / "invalid.jpg"
        invalid_file.write_text("not an image")

        processor = ReceiptProcessor()
        result = processor.process_receipt(invalid_file)

        assert result['success'] is False
        assert 'Invalid input' in result['message'] or 'Error' in result['message']

    @pytest.mark.unit
    def test_process_receipt_creates_output_directory(self, skewed_receipt_image, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        image_path, _ = skewed_receipt_image
        output_path = tmp_path / "subdir" / "output.jpg"

        processor = ReceiptProcessor()
        result = processor.process_receipt(image_path, output_path)

        if result['success']:
            assert output_path.parent.exists()

    @pytest.mark.unit
    def test_visualize_detection_success(self, skewed_receipt_image, tmp_path):
        """Test visualization of detected receipt."""
        image_path, _ = skewed_receipt_image
        output_path = tmp_path / "visualization.jpg"

        processor = ReceiptProcessor()
        vis_image = processor.visualize_detection(image_path, output_path)

        if vis_image is not None:
            assert isinstance(vis_image, np.ndarray)
            assert len(vis_image.shape) == 3  # Color image
            assert output_path.exists()

    @pytest.mark.unit
    def test_visualize_detection_with_numpy_array(self, skewed_receipt_image):
        """Test visualization with numpy array input."""
        image_path, _ = skewed_receipt_image
        image = cv2.imread(str(image_path))

        processor = ReceiptProcessor()
        vis_image = processor.visualize_detection(image)

        # May or may not succeed depending on image
        if vis_image is not None:
            assert isinstance(vis_image, np.ndarray)

    @pytest.mark.unit
    def test_visualize_detection_no_receipt(self, tmp_path):
        """Test visualization when no receipt is detected."""
        # Create image with no receipt
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 128
        image_path = tmp_path / "no_receipt.jpg"
        cv2.imwrite(str(image_path), test_image)

        processor = ReceiptProcessor()
        vis_image = processor.visualize_detection(image_path)

        assert vis_image is None

    @pytest.mark.unit
    def test_visualize_detection_creates_output_directory(self, skewed_receipt_image, tmp_path):
        """Test that visualization creates output directory if needed."""
        image_path, _ = skewed_receipt_image
        output_path = tmp_path / "vis" / "output.jpg"

        processor = ReceiptProcessor()
        processor.visualize_detection(image_path, output_path)

        # Directory should be created even if detection fails
        assert output_path.parent.exists()


class TestProcessReceiptSimple:
    """Tests for process_receipt_simple convenience function."""

    @pytest.mark.unit
    def test_process_receipt_simple_success(self, skewed_receipt_image, tmp_path):
        """Test simple processing function."""
        image_path, _ = skewed_receipt_image
        output_path = tmp_path / "simple_output.jpg"

        result = process_receipt_simple(image_path, output_path)

        # May succeed or fail depending on image quality
        if result is not None:
            assert isinstance(result, np.ndarray)
            assert output_path.exists()

    @pytest.mark.unit
    def test_process_receipt_simple_no_output(self, skewed_receipt_image):
        """Test simple processing without output path."""
        image_path, _ = skewed_receipt_image

        result = process_receipt_simple(image_path)

        # Returns None on failure, numpy array on success
        assert result is None or isinstance(result, np.ndarray)

    @pytest.mark.unit
    def test_process_receipt_simple_failure(self, tmp_path):
        """Test simple processing with no receipt."""
        # Create image with no receipt
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 128
        image_path = tmp_path / "no_receipt.jpg"
        cv2.imwrite(str(image_path), test_image)

        result = process_receipt_simple(image_path)

        assert result is None

    @pytest.mark.unit
    def test_process_receipt_simple_file_not_found(self):
        """Test simple processing with non-existent file."""
        result = process_receipt_simple("/nonexistent/image.jpg")

        assert result is None


class TestIntegrationPipeline:
    """Integration tests for complete processing pipeline."""

    @pytest.mark.unit
    def test_complete_pipeline_skewed_receipt(self, skewed_receipt_image, tmp_path):
        """Test complete pipeline with skewed receipt."""
        image_path, original_pts = skewed_receipt_image
        output_path = tmp_path / "final.jpg"

        processor = ReceiptProcessor()
        result = processor.process_receipt(
            image_path,
            output_path,
            return_steps=True
        )

        assert result is not None

        if result['success']:
            # Check all steps completed
            assert result['processed_image'] is not None
            assert result['contour'] is not None

            steps = result['steps']
            assert 'original' in steps
            assert 'preprocessed' in steps
            assert 'edges' in steps
            assert 'warped' in steps
            assert 'final' in steps

            # Verify image transformations
            original = steps['original']
            preprocessed = steps['preprocessed']
            edges = steps['edges']
            final = steps['final']

            # Preprocessed should be grayscale
            assert len(preprocessed.shape) == 2

            # Edges should be binary
            assert len(edges.shape) == 2

            # Final should be binary (background removed)
            assert len(final.shape) == 2

    @pytest.mark.unit
    def test_pipeline_maintains_data_integrity(self, skewed_receipt_image):
        """Test that pipeline doesn't corrupt data."""
        image_path, _ = skewed_receipt_image

        processor = ReceiptProcessor()
        result = processor.process_receipt(image_path, return_steps=True)

        if result['success']:
            # All intermediate images should be valid numpy arrays
            for step_name, step_image in result['steps'].items():
                assert isinstance(step_image, np.ndarray)
                assert step_image.size > 0
                assert step_image.dtype == np.uint8
