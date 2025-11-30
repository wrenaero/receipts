#!/usr/bin/env python3
"""
Simple CLI for scanning receipts.
Works without needing to start the API server.

Usage:
    python scan_receipt.py receipt.jpg output.jpg
    python scan_receipt.py receipt.jpg output.jpg --ocr
    python scan_receipt.py receipt.jpg output.jpg --visualize
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.services.image_processor import ReceiptProcessor
from src.services.ocr_service import OCRService
import json


def main():
    parser = argparse.ArgumentParser(description='Scan and process receipt images')
    parser.add_argument('input', help='Input receipt image')
    parser.add_argument('output', nargs='?', help='Output file (optional)')
    parser.add_argument('--ocr', action='store_true', help='Extract text using OCR')
    parser.add_argument('--visualize', action='store_true', help='Visualize detection instead of processing')
    parser.add_argument('--min-area', type=float, default=0.01,
                       help='Minimum receipt area %% (default: 0.01 for small receipts)')
    parser.add_argument('--tolerance', type=float, default=0.05,
                       help='Contour approximation tolerance (default: 0.05 for complex edges)')

    args = parser.parse_args()

    # Default output filename
    if not args.output:
        input_path = Path(args.input)
        if args.visualize:
            args.output = f"visualization_{input_path.name}"
        else:
            args.output = f"processed_{input_path.name}"

    processor = ReceiptProcessor()

    if args.visualize:
        # Visualize detection
        print(f"🔍 Visualizing receipt detection...")
        print(f"   Input: {args.input}")
        print(f"   Parameters: min_area={args.min_area}%, tolerance={args.tolerance}")

        vis = processor.visualize_detection(
            args.input,
            args.output,
            min_area_percent=args.min_area,
            approx_tolerance=args.tolerance
        )

        if vis is not None:
            print(f"✅ Visualization saved to: {args.output}")
            return 0
        else:
            print(f"❌ Could not detect receipt")
            print(f"\n💡 Try adjusting parameters:")
            print(f"   --min-area 0.001   (for very small receipts)")
            print(f"   --tolerance 0.1    (for very complex edges)")
            return 1
    else:
        # Process receipt
        print(f"📄 Processing receipt...")
        print(f"   Input: {args.input}")
        print(f"   Output: {args.output}")
        print(f"   Parameters: min_area={args.min_area}%, tolerance={args.tolerance}")

        result = processor.process_receipt(
            args.input,
            args.output,
            min_area_percent=args.min_area,
            approx_tolerance=args.tolerance
        )

        if not result['success']:
            print(f"❌ Failed: {result['message']}")
            print(f"\n💡 Try adjusting parameters:")
            print(f"   --min-area 0.001   (for very small receipts)")
            print(f"   --tolerance 0.1    (for very complex edges)")
            print(f"\nOr visualize to debug:")
            print(f"   python scan_receipt.py {args.input} debug.jpg --visualize")
            return 1

        print(f"✅ Receipt processed successfully!")
        print(f"   Saved to: {args.output}")

        # OCR if requested
        if args.ocr:
            print(f"\n🔤 Extracting text with OCR...")
            try:
                ocr = OCRService()
                data = ocr.extract_structured_data(result['processed_image'])

                print(f"\n📊 Extracted Data:")
                print(f"   Merchant: {data.get('merchant', 'Not found')}")
                print(f"   Date: {data.get('date', 'Not found')}")
                print(f"   Total: ${data.get('total', 'Not found')}")

                if data.get('items'):
                    print(f"   Items:")
                    for item in data['items'][:5]:  # Show first 5 items
                        print(f"      - {item}")

                # Save OCR data
                ocr_output = Path(args.output).stem + "_ocr.json"
                with open(ocr_output, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\n💾 OCR data saved to: {ocr_output}")

            except Exception as e:
                print(f"⚠️  OCR failed: {str(e)}")

        return 0


if __name__ == "__main__":
    sys.exit(main())
