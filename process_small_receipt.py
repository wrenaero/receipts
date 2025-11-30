#!/usr/bin/env python3
"""
Process receipts that are small in the frame by using a lower area threshold.
Usage: python process_small_receipt.py <input_image> [output_image]
"""

import sys
import cv2
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.image_utils import load_image, preprocess_image, detect_edges, order_points
from src.services.receipt_detector import four_point_transform, remove_background


def find_receipt_contour_small(edged_image, min_area_percent=0.01):
    """
    Find receipt contour with a much lower area threshold for small receipts.

    Args:
        edged_image: Edge-detected image
        min_area_percent: Minimum area as percentage of image (default 0.01% = 1/100th of 1%)
    """
    contours, _ = cv2.findContours(edged_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Sort by area
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

    image_area = edged_image.shape[0] * edged_image.shape[1]
    min_area = image_area * (min_area_percent / 100)

    print(f"Looking for contours >= {min_area_percent}% of image area ({min_area:.0f} pixels)")
    print(f"Checking top {min(len(sorted_contours), 20)} contours...")

    # Check top 20 contours
    for i, contour in enumerate(sorted_contours[:20], 1):
        area = cv2.contourArea(contour)
        area_pct = (area / image_area) * 100

        # Approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        num_sides = len(approx)

        print(f"  {i}. Area: {area:>8.0f} ({area_pct:>5.2f}%) | Sides: {num_sides}", end="")

        # Look for quadrilaterals (4 sides) that meet minimum area
        if num_sides == 4 and area >= min_area:
            print(" ✅ SELECTED")
            return approx.reshape(4, 2)
        else:
            print()

    print("\n⚠️  No suitable 4-sided contour found")
    return None


def process_small_receipt(image_path, output_path=None, min_area_percent=0.01):
    """
    Process a receipt that's small in the frame.

    Args:
        image_path: Path to input image
        output_path: Path to save output (optional)
        min_area_percent: Minimum area threshold (default 0.01%)
    """
    print(f"📄 Processing small receipt: {image_path}")
    print(f"   Min area threshold: {min_area_percent}%\n")

    # Load and preprocess
    image = load_image(image_path, max_dimension=1000)
    print(f"✅ Loaded image: {image.shape[1]} x {image.shape[0]}")

    preprocessed = preprocess_image(image)
    print(f"✅ Preprocessed image")

    # Detect edges
    edges = detect_edges(preprocessed)
    print(f"✅ Detected edges\n")

    # Find receipt contour with low threshold
    contour = find_receipt_contour_small(edges, min_area_percent)

    if contour is None:
        print("\n❌ Could not find receipt in image")
        print("\n💡 Try:")
        print("   1. Use an even lower threshold: python process_small_receipt.py receipt.jpg output.jpg 0.005")
        print("   2. Crop the image to just the receipt area")
        print("   3. Retake the photo closer to the receipt")
        return None

    print(f"\n✅ Found receipt contour")

    # Order points and apply perspective transform
    ordered_contour = order_points(contour)
    warped = four_point_transform(image, ordered_contour)
    print(f"✅ Applied perspective transform: {warped.shape[1]} x {warped.shape[0]}")

    # Remove background
    cleaned = remove_background(warped)
    print(f"✅ Removed background")

    # Save output
    if output_path:
        cv2.imwrite(output_path, cleaned)
        print(f"\n💾 Saved to: {output_path}")

    return cleaned


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_small_receipt.py <input_image> [output_image] [min_area_percent]")
        print("\nExamples:")
        print("  python process_small_receipt.py receipt.jpg")
        print("  python process_small_receipt.py receipt.jpg processed.jpg")
        print("  python process_small_receipt.py receipt.jpg processed.jpg 0.005")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "processed_receipt.jpg"
    min_area = float(sys.argv[3]) if len(sys.argv) > 3 else 0.01

    result = process_small_receipt(input_path, output_path, min_area)

    if result is not None:
        print("\n✅ SUCCESS! Receipt processed successfully")
        print(f"\nTo view: open {output_path}")
    else:
        print("\n❌ FAILED to process receipt")
        sys.exit(1)
