#!/usr/bin/env python3
"""Create a test receipt image for testing the scanner."""

import cv2
import numpy as np

# Create a test receipt image
# White receipt on dark background with clear edges

# Create canvas (dark gray background)
img = np.ones((800, 600, 3), dtype=np.uint8) * 50

# Draw white receipt rectangle
receipt_pts = np.array([
    [150, 100],   # top-left
    [450, 120],   # top-right
    [440, 650],   # bottom-right
    [160, 630]    # bottom-left
], dtype=np.int32)

# Fill the receipt area with white
cv2.fillPoly(img, [receipt_pts], (255, 255, 255))

# Add some "text" lines to make it look like a receipt
for i in range(15):
    y = 180 + i * 30
    cv2.line(img, (180, y), (420, y), (0, 0, 0), 2)

# Add a "header"
cv2.rectangle(img, (180, 130), (420, 160), (100, 100, 100), -1)

# Save the test image
cv2.imwrite('test_receipt.jpg', img)

print("✅ Test receipt created: test_receipt.jpg")
print("\nThis image has:")
print("- Clear white receipt on dark background")
print("- Distinct edges")
print("- Slight skew to test deskewing")
print("\nTry scanning it with:")
print('curl -X POST "http://localhost:8000/api/v1/scan" -F "file=@test_receipt.jpg"')
