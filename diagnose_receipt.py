#!/usr/bin/env python3
"""
Diagnostic tool to analyze why a receipt image isn't being detected.
Usage: python diagnose_receipt.py <image_path>
"""

import sys
import cv2
import numpy as np
from pathlib import Path

def diagnose_receipt_image(image_path):
    """Comprehensive diagnostic of receipt detection issues."""

    print(f"📊 RECEIPT DETECTION DIAGNOSTICS")
    print(f"=" * 60)
    print(f"Image: {image_path}\n")

    # Check file exists
    if not Path(image_path).exists():
        print(f"❌ ERROR: File not found: {image_path}")
        return

    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"❌ ERROR: Could not load image (corrupted or unsupported format)")
        return

    h, w = img.shape[:2]
    total_pixels = h * w

    print(f"✅ Image loaded successfully")
    print(f"   Size: {w} x {h} pixels")
    print(f"   Total pixels: {total_pixels:,}")
    print(f"   Aspect ratio: {w/h:.2f}")
    print()

    # Resize if too large
    max_dim = 1000
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img_resized = cv2.resize(img, (new_w, new_h))
        print(f"🔽 Image resized for processing: {new_w} x {new_h}")
        print()
    else:
        img_resized = img
        new_h, new_w = h, w

    # Convert to grayscale
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

    # Analyze brightness and contrast
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)
    min_brightness = np.min(gray)
    max_brightness = np.max(gray)

    print(f"🔆 BRIGHTNESS & CONTRAST")
    print(f"   Mean brightness: {mean_brightness:.1f} (ideal: 100-150)")
    print(f"   Std deviation: {std_brightness:.1f} (ideal: >40 for good contrast)")
    print(f"   Range: {min_brightness} - {max_brightness}")

    if std_brightness < 30:
        print(f"   ⚠️  WARNING: Low contrast image")
    if mean_brightness < 80:
        print(f"   ⚠️  WARNING: Dark image")
    elif mean_brightness > 180:
        print(f"   ⚠️  WARNING: Very bright image (possibly overexposed)")
    print()

    # Edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    edge_pixels = np.count_nonzero(edges)
    edge_percentage = (edge_pixels / (new_h * new_w)) * 100

    print(f"🔍 EDGE DETECTION")
    print(f"   Edge pixels: {edge_pixels:,}")
    print(f"   Edge percentage: {edge_percentage:.2f}%")

    if edge_percentage < 1:
        print(f"   ⚠️  WARNING: Very few edges detected (image may be too blurry)")
    elif edge_percentage > 15:
        print(f"   ⚠️  WARNING: Too many edges (complex background?)")
    print()

    # Contour detection
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"📐 CONTOUR ANALYSIS")
    print(f"   Total contours found: {len(contours)}")

    # Sort by area
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    image_area = new_h * new_w
    min_receipt_area = image_area * 0.05  # 5% minimum

    print(f"   Image area: {image_area:,} pixels")
    print(f"   Minimum receipt area (5%): {min_receipt_area:,.0f} pixels")
    print()

    print(f"   Top 10 contours by area:")
    receipt_found = False

    for i, contour in enumerate(sorted_contours[:10], 1):
        area = cv2.contourArea(contour)
        area_pct = (area / image_area) * 100
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        num_sides = len(approx)

        status = ""
        if num_sides == 4 and area >= min_receipt_area:
            status = " ✅ RECEIPT CANDIDATE"
            receipt_found = True
        elif num_sides == 4:
            status = " ⚠️  4-sided but too small"

        print(f"   {i}. Area: {area:>10,.0f} ({area_pct:>5.2f}%) | Sides: {num_sides}{status}")

    print()

    if receipt_found:
        print(f"✅ LIKELY DETECTABLE: Found 4-sided contour(s) ≥5% of image area")
        print(f"   The receipt should be detectable with the current algorithm.")
    else:
        print(f"❌ NOT DETECTABLE with current settings")
        print(f"\n💡 RECOMMENDATIONS:")

        if edge_percentage < 1:
            print(f"   1. Try enhancing the image:")
            print(f"      python enhance_receipt.py {image_path} enhanced.jpg")

        if mean_brightness < 100:
            print(f"   2. Image is too dark - retake with better lighting")

        if std_brightness < 30:
            print(f"   3. Low contrast - try placing receipt on contrasting background")

        largest_area_pct = (cv2.contourArea(sorted_contours[0]) / image_area * 100) if sorted_contours else 0
        if largest_area_pct < 5:
            print(f"   4. Receipt is too small in frame - get closer when taking photo")

        has_quad = any(len(cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)) == 4
                      for c in sorted_contours[:5])
        if not has_quad:
            print(f"   5. No clear rectangular shape detected - ensure receipt has straight edges")
            print(f"      and is on a plain background")

    print()

    # Save diagnostic images
    output_dir = Path("diagnostics")
    output_dir.mkdir(exist_ok=True)

    # Save edges
    edges_path = output_dir / f"edges_{Path(image_path).stem}.jpg"
    cv2.imwrite(str(edges_path), edges)
    print(f"💾 Saved edge detection: {edges_path}")

    # Draw top 3 contours
    viz = img_resized.copy()
    for i, contour in enumerate(sorted_contours[:3]):
        color = [(0, 255, 0), (0, 165, 255), (0, 0, 255)][i]  # Green, Orange, Red
        cv2.drawContours(viz, [contour], -1, color, 3)

        # Label with number
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(viz, f"#{i+1}", (cx-20, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    viz_path = output_dir / f"contours_{Path(image_path).stem}.jpg"
    cv2.imwrite(str(viz_path), viz)
    print(f"💾 Saved contour visualization: {viz_path}")

    print()
    print(f"=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_receipt.py <image_path>")
        sys.exit(1)

    diagnose_receipt_image(sys.argv[1])
