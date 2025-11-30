#!/usr/bin/env python3
"""
Simple receipt data extraction.
For skew correction, run this first if needed.
"""

import sys
import json
import cv2
import numpy as np
from pathlib import Path


def deskew_image(image):
    """Simple deskew using document contours."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur and threshold
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Find contours
    coords = np.column_stack(np.where(thresh > 0))

    # Get rotation angle
    angle = cv2.minAreaRect(coords)[-1]

    # Correct angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Rotate
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated, angle


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_extract.py <input_image> [output_deskewed.jpg]")
        print("\nThis will:")
        print("  1. Deskew the image")
        print("  2. Save the corrected image")
        print("  3. Extract text if PaddleOCR is available")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "deskewed.jpg"

    print(f"📄 Processing: {input_path}")

    # Load image
    image = cv2.imread(input_path)
    if image is None:
        print(f"❌ Could not load image")
        sys.exit(1)

    print(f"✅ Loaded: {image.shape[1]} x {image.shape[0]} pixels")

    # Deskew
    print(f"🔄 Correcting skew...")
    try:
        deskewed, angle = deskew_image(image)
        print(f"   Rotation applied: {angle:.2f}°")

        # Save deskewed image
        cv2.imwrite(output_path, deskewed)
        print(f"💾 Saved deskewed image: {output_path}")

    except Exception as e:
        print(f"⚠️  Deskew failed: {e}")
        print(f"   Saving original image instead...")
        cv2.imwrite(output_path, image)

    # Try OCR if available
    print(f"\n🔤 Attempting text extraction...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.services.ocr_service import OCRService

        ocr = OCRService()
        result = ocr.extract_structured_data(deskewed)

        # Save JSON
        json_path = Path(output_path).stem + "_data.json"
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"✅ OCR completed!")
        print(f"   Merchant: {result.get('merchant', 'N/A')}")
        print(f"   Date: {result.get('date', 'N/A')}")
        print(f"   Total: ${result.get('total', 'N/A')}")
        print(f"💾 JSON saved: {json_path}")

    except ImportError:
        print(f"⚠️  PaddleOCR not available")
        print(f"\nTo extract text data, install OCR:")
        print(f"   pip install paddlepaddle paddleocr")
        print(f"\nThen run:")
        print(f"   python extract_receipt_data.py {output_path} output.json")
    except Exception as e:
        print(f"⚠️  OCR error: {e}")

    print(f"\n✅ Done! Deskewed image saved to: {output_path}")


if __name__ == "__main__":
    main()
