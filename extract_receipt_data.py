#!/usr/bin/env python3
"""
Extract receipt data to JSON without requiring perfect detection.
Works with receipts on any background.

Usage:
    python extract_receipt_data.py receipt.jpg output.json
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.services.ocr_service import OCRService
import cv2


def extract_data(image_path, output_json=None):
    """Extract text and structured data from receipt image."""

    print(f"📄 Extracting data from: {image_path}")

    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return None

    print(f"✅ Image loaded: {image.shape[1]} x {image.shape[0]} pixels")

    # Extract text with OCR
    print(f"🔤 Running OCR...")
    try:
        ocr = OCRService()
        data = ocr.extract_structured_data(image)

        print(f"\n📊 Extracted Data:")
        print(f"   Merchant: {data.get('merchant', 'Not found')}")
        print(f"   Date: {data.get('date', 'Not found')}")
        print(f"   Total: ${data.get('total', 'Not found')}")

        if data.get('items'):
            print(f"   Items found: {len(data['items'])}")
            for i, item in enumerate(data['items'][:3], 1):
                print(f"      {i}. {item}")
            if len(data['items']) > 3:
                print(f"      ... and {len(data['items']) - 3} more")

        # Add image metadata
        data['_metadata'] = {
            'source_file': str(image_path),
            'image_size': f"{image.shape[1]}x{image.shape[0]}",
        }

        # Save to JSON
        if output_json is None:
            output_json = Path(image_path).stem + "_data.json"

        with open(output_json, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n💾 Data saved to: {output_json}")

        # Also print full raw text
        print(f"\n📝 Raw text ({len(data.get('raw_text', []))} lines):")
        for line in data.get('raw_text', [])[:20]:
            print(f"   {line}")
        if len(data.get('raw_text', [])) > 20:
            print(f"   ... and {len(data.get('raw_text', [])) - 20} more lines")

        return data

    except Exception as e:
        print(f"❌ OCR failed: {str(e)}")
        print(f"\nMake sure PaddleOCR is installed:")
        print(f"   pip install paddlepaddle paddleocr")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Extract receipt data to JSON')
    parser.add_argument('input', help='Input receipt image')
    parser.add_argument('output', nargs='?', help='Output JSON file (optional)')

    args = parser.parse_args()

    result = extract_data(args.input, args.output)

    if result:
        print(f"\n✅ SUCCESS!")
        sys.exit(0)
    else:
        print(f"\n❌ FAILED")
        sys.exit(1)
