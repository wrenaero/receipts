"""Receipt detection and extraction service."""

import cv2
import numpy as np
from typing import Optional, Tuple

from src.utils.image_utils import order_points


def find_receipt_contour(edged_image: np.ndarray) -> Optional[np.ndarray]:
    """
    Find the largest rectangular contour in an edge-detected image.

    This function attempts to find a receipt by looking for the largest
    4-sided contour in the image.

    Args:
        edged_image: Edge-detected binary image

    Returns:
        numpy.ndarray or None: Array of 4 corner points if found, None otherwise
                               Shape: (4, 1, 2) or (4, 2)

    Raises:
        ValueError: If image is invalid
    """
    if edged_image is None or edged_image.size == 0:
        raise ValueError("Invalid image: empty or None")

    # Find contours
    contours, _ = cv2.findContours(
        edged_image.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    # Sort contours by area (largest first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Look for a 4-sided contour (receipt should be rectangular)
    for contour in contours[:10]:  # Check top 10 largest contours
        # Calculate perimeter
        peri = cv2.arcLength(contour, True)

        # Approximate the contour
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # Receipt should have 4 corners
        if len(approx) == 4:
            # Additional validation: check if contour is large enough
            area = cv2.contourArea(approx)
            image_area = edged_image.shape[0] * edged_image.shape[1]

            # Receipt should be at least 5% of image area
            if area > image_area * 0.05:
                return approx

    return None


def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """
    Apply perspective transformation to obtain a bird's-eye view of the receipt.

    This function takes four corner points of a receipt and transforms the
    perspective to create a rectangular, top-down view.

    Args:
        image: Original image
        pts: Array of 4 corner points, shape (4, 2) or (4, 1, 2)

    Returns:
        numpy.ndarray: Warped image with corrected perspective

    Raises:
        ValueError: If image or points are invalid
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image: empty or None")

    if pts is None or pts.size == 0:
        raise ValueError("Invalid points: empty or None")

    # Order the points
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # Compute the width of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # Compute the height of the new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # Ensure minimum dimensions
    if maxWidth < 10 or maxHeight < 10:
        raise ValueError("Computed dimensions too small")

    # Destination points for the perspective transform
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    # Compute the perspective transform matrix
    M = cv2.getPerspectiveTransform(rect, dst)

    # Apply the perspective transformation
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def remove_background(image: np.ndarray) -> np.ndarray:
    """
    Remove background and enhance receipt for better OCR results.

    Applies adaptive thresholding and morphological operations to clean up
    the receipt image.

    Args:
        image: Input image (color or grayscale)

    Returns:
        numpy.ndarray: Cleaned binary image

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

    # Apply adaptive thresholding
    # This works better than global thresholding for receipts with varying lighting
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,  # Block size
        2    # Constant subtracted from mean
    )

    # Morphological operations to remove noise
    # Use a small kernel to avoid removing text
    kernel = np.ones((2, 2), np.uint8)

    # Close small holes in the text
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Remove small noise
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)

    return cleaned


def detect_and_extract_receipt(
    image: np.ndarray,
    edged_image: np.ndarray,
    apply_background_removal: bool = True
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Detect receipt in image and extract it with perspective correction.

    Args:
        image: Original color image
        edged_image: Edge-detected version of the image
        apply_background_removal: Whether to apply background removal

    Returns:
        Tuple of (warped_image, contour):
            - warped_image: Perspective-corrected receipt (or None if not found)
            - contour: The detected receipt contour (or None if not found)
    """
    # Find receipt contour
    contour = find_receipt_contour(edged_image)

    if contour is None:
        return None, None

    # Apply perspective transformation
    warped = four_point_transform(image, contour.reshape(4, 2))

    # Apply background removal if requested
    if apply_background_removal:
        warped = remove_background(warped)

    return warped, contour
