#!/usr/bin/env python3
"""Enhance receipt image for better detection."""

import cv2
import numpy as np
import sys

if len(sys.argv) != 3:
    print("Usage: python enhance_receipt.py input.jpg output.jpg")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Read image
img = cv2.imread(input_file)
if img is None:
    print(f"Error: Could not read {input_file}")
    sys.exit(1)

# Enhance contrast
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)

# Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
l = clahe.apply(l)

# Merge channels
enhanced = cv2.merge([l, a, b])
enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

# Sharpen
kernel = np.array([[-1,-1,-1],
                   [-1, 9,-1],
                   [-1,-1,-1]])
sharpened = cv2.filter2D(enhanced, -1, kernel)

# Save
cv2.imwrite(output_file, sharpened)
print(f"✅ Enhanced image saved to: {output_file}")
print(f"\nTry scanning it with:")
print(f'curl -X POST "http://localhost:8000/api/v1/scan" -F "file=@{output_file}"')
