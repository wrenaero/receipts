"""Main image processing pipeline for receipt scanning."""

import cv2
import numpy as np
from pathlib import Path
from typing import Union, Optional, Dict, Any

from src.utils.image_utils import (
    load_image,
    preprocess_image,
    detect_edges
)
from src.services.receipt_detector import (
    find_receipt_contour,
    four_point_transform,
    remove_background,
    detect_and_extract_receipt
)


class ReceiptProcessor:
    """Main class for processing receipt images."""

    def __init__(self):
        """Initialize the receipt processor."""
        self.last_result = None

    def process_receipt(
        self,
        image_path: Union[str, Path, np.ndarray],
        output_path: Optional[Union[str, Path]] = None,
        return_steps: bool = False
    ) -> Dict[str, Any]:
        """
        Complete receipt processing pipeline.

        This method handles the entire workflow:
        1. Load image
        2. Preprocess (grayscale, blur)
        3. Detect edges
        4. Find receipt contour
        5. Apply perspective transformation (deskew)
        6. Remove background and cleanup

        Args:
            image_path: Path to image file or numpy array
            output_path: Optional path to save processed image
            return_steps: If True, return intermediate processing steps

        Returns:
            Dict containing:
                - success: bool
                - processed_image: numpy array or None
                - contour: detected contour or None
                - message: status message
                - steps: dict of intermediate steps (if return_steps=True)

        Example:
            >>> processor = ReceiptProcessor()
            >>> result = processor.process_receipt("receipt.jpg", "output.jpg")
            >>> if result['success']:
            >>>     print("Receipt processed successfully!")
        """
        steps = {} if return_steps else None

        try:
            # Step 1: Load image
            if isinstance(image_path, np.ndarray):
                original = image_path.copy()
            else:
                original = load_image(image_path)

            if return_steps:
                steps['original'] = original.copy()

            # Step 2: Preprocess
            preprocessed = preprocess_image(original)

            if return_steps:
                steps['preprocessed'] = preprocessed.copy()

            # Step 3: Detect edges
            edges = detect_edges(preprocessed)

            if return_steps:
                steps['edges'] = edges.copy()

            # Step 4: Find receipt contour
            contour = find_receipt_contour(edges)

            if contour is None:
                return {
                    'success': False,
                    'processed_image': None,
                    'contour': None,
                    'message': 'Could not detect receipt in image',
                    'steps': steps
                }

            if return_steps:
                steps['contour'] = contour.copy()

            # Step 5: Apply perspective transformation (deskew)
            warped = four_point_transform(original, contour.reshape(4, 2))

            if return_steps:
                steps['warped'] = warped.copy()

            # Step 6: Remove background and cleanup
            final = remove_background(warped)

            if return_steps:
                steps['final'] = final.copy()

            # Save if output path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(output_path), final)

            # Store last result
            self.last_result = {
                'processed_image': final,
                'contour': contour,
                'original': original
            }

            return {
                'success': True,
                'processed_image': final,
                'contour': contour,
                'message': 'Receipt processed successfully',
                'steps': steps
            }

        except FileNotFoundError as e:
            return {
                'success': False,
                'processed_image': None,
                'contour': None,
                'message': f'File not found: {str(e)}',
                'steps': steps
            }

        except ValueError as e:
            return {
                'success': False,
                'processed_image': None,
                'contour': None,
                'message': f'Invalid input: {str(e)}',
                'steps': steps
            }

        except Exception as e:
            return {
                'success': False,
                'processed_image': None,
                'contour': None,
                'message': f'Error processing receipt: {str(e)}',
                'steps': steps
            }

    def visualize_detection(
        self,
        image_path: Union[str, Path, np.ndarray],
        output_path: Optional[Union[str, Path]] = None
    ) -> Optional[np.ndarray]:
        """
        Visualize the receipt detection by drawing the detected contour.

        Args:
            image_path: Path to image file or numpy array
            output_path: Optional path to save visualization

        Returns:
            Image with contour drawn, or None if detection failed
        """
        try:
            # Load image
            if isinstance(image_path, np.ndarray):
                original = image_path.copy()
            else:
                original = load_image(image_path)

            # Process to get contour
            preprocessed = preprocess_image(original)
            edges = detect_edges(preprocessed)
            contour = find_receipt_contour(edges)

            if contour is None:
                return None

            # Draw contour on original image
            vis_image = original.copy()
            cv2.drawContours(vis_image, [contour], -1, (0, 255, 0), 3)

            # Draw corner points
            for point in contour.reshape(4, 2):
                cv2.circle(vis_image, tuple(point.astype(int)), 8, (0, 0, 255), -1)

            # Save if output path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(output_path), vis_image)

            return vis_image

        except Exception as e:
            # Still create directory even if visualization fails
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
            return None


def process_receipt_simple(
    image_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None
) -> Optional[np.ndarray]:
    """
    Simplified function to process a single receipt.

    This is a convenience function that wraps ReceiptProcessor
    for simple use cases.

    Args:
        image_path: Path to the receipt image
        output_path: Optional path to save processed image

    Returns:
        Processed image as numpy array, or None if processing failed

    Example:
        >>> processed = process_receipt_simple("receipt.jpg", "output.jpg")
        >>> if processed is not None:
        >>>     print("Success!")
    """
    processor = ReceiptProcessor()
    result = processor.process_receipt(image_path, output_path)

    if result['success']:
        return result['processed_image']
    else:
        return None
