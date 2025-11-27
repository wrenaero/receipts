# Receipt Scanning Implementation Guide

**Created:** 2025-11-27
**Status:** Planning
**Priority:** High

## Overview

Build an intelligent receipt scanning online application that can automatically process receipt images by:
- Removing unrelated borders and backgrounds
- Fixing image skewness (deskewing)
- Detecting and cropping only the receipt portion
- Preparing images for OCR text extraction

## Technology Stack

### Recommended Programming Language: **Python**

Python is the ideal choice for this task because:
- **Rich ecosystem** of computer vision and ML libraries
- **OpenCV** has excellent Python bindings
- **Easy integration** with OCR engines
- **Rapid prototyping** and development
- **Strong community** support for document processing
- **Web framework** options (Flask, FastAPI, Django) for online app

### Core Libraries

#### 1. **opencv-python** (OpenCV)
- **Purpose:** Image processing, cropping, deskewing, perspective correction
- **Key Functions:**
  - Edge detection (Canny)
  - Contour detection
  - Perspective transformation
  - Image rotation and alignment
  - Noise reduction and preprocessing

```bash
pip install opencv-python
```

#### 2. **numpy**
- **Purpose:** Numerical operations, array manipulation
- **Use Cases:**
  - Image array transformations
  - Mathematical operations for perspective correction
  - Efficient data handling

```bash
pip install numpy
```

### Optional ML/OCR Stack

#### 3. **PaddleOCR** (Recommended)
- **Purpose:** OCR text extraction with high accuracy
- **Advantages:**
  - Multi-language support
  - Pre-trained models
  - Good performance on receipts
  - Both detection and recognition

```bash
pip install paddlepaddle paddleocr
```

#### 4. **Tesseract OCR**
- **Purpose:** Alternative OCR engine
- **Advantages:**
  - Open-source and well-established
  - Highly customizable
  - Multiple language support

```bash
pip install pytesseract
# Also requires Tesseract binary installation
```

#### 5. **docTR** (Document Text Recognition)
- **Purpose:** Modern deep learning-based OCR
- **Advantages:**
  - PyTorch/TensorFlow backends
  - State-of-the-art accuracy
  - Document-specific optimization

```bash
pip install python-doctr
```

#### 6. **YOLO (You Only Look Once)**
- **Purpose:** Receipt/document detection
- **Use Cases:**
  - Detecting receipt boundaries in complex images
  - Real-time object detection
  - Training custom models for receipt detection

```bash
pip install ultralytics  # YOLOv8
```

## Implementation Approach

### Phase 1: Image Preprocessing Pipeline

#### Step 1: Load and Resize Image
```python
import cv2
import numpy as np

def load_image(image_path):
    """Load and optionally resize image for processing"""
    image = cv2.imread(image_path)
    # Resize if too large (maintain aspect ratio)
    height, width = image.shape[:2]
    max_dimension = 1500
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        image = cv2.resize(image, None, fx=scale, fy=scale)
    return image
```

#### Step 2: Convert to Grayscale and Apply Preprocessing
```python
def preprocess_image(image):
    """Convert to grayscale and apply preprocessing"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred
```

#### Step 3: Edge Detection
```python
def detect_edges(image):
    """Detect edges using Canny edge detection"""
    edged = cv2.Canny(image, 75, 200)
    return edged
```

#### Step 4: Find Receipt Contours
```python
def find_receipt_contour(edged_image):
    """Find the largest rectangular contour (likely the receipt)"""
    contours, _ = cv2.findContours(
        edged_image.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Sort contours by area (largest first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    receipt_contour = None
    for contour in contours:
        # Approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # Receipt should have 4 corners
        if len(approx) == 4:
            receipt_contour = approx
            break

    return receipt_contour
```

#### Step 5: Perspective Transformation (Deskewing)
```python
def order_points(pts):
    """Order points in consistent order: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")

    # Sum and difference to find corners
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]      # top-left
    rect[2] = pts[np.argmax(s)]      # bottom-right
    rect[1] = pts[np.argmin(diff)]   # top-right
    rect[3] = pts[np.argmax(diff)]   # bottom-left

    return rect

def four_point_transform(image, pts):
    """Apply perspective transformation to get bird's eye view"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # Compute width of new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # Compute height of new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # Destination points for perspective transform
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    # Compute perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped
```

#### Step 6: Background Removal and Cleanup
```python
def remove_background(image):
    """Remove background and enhance receipt"""
    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    # Optional: morphological operations to clean up
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return cleaned
```

### Phase 2: ML-Enhanced Detection (Optional)

#### Using YOLO for Receipt Detection
```python
from ultralytics import YOLO

def detect_receipt_with_yolo(image_path, model_path='yolov8n.pt'):
    """Use YOLO to detect receipt in image"""
    model = YOLO(model_path)
    results = model(image_path)

    # Get bounding box of detected receipt
    for result in results:
        boxes = result.boxes
        for box in boxes:
            if box.conf > 0.5:  # Confidence threshold
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                return (int(x1), int(y1), int(x2), int(y2))

    return None
```

#### Using PaddleOCR
```python
from paddleocr import PaddleOCR

def extract_text_paddleocr(image_path):
    """Extract text from receipt using PaddleOCR"""
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(image_path, cls=True)

    # Extract text lines
    text_lines = []
    for line in result[0]:
        text_lines.append(line[1][0])  # line[1][0] contains the text

    return text_lines
```

### Phase 3: Complete Pipeline

```python
def process_receipt(image_path, output_path=None):
    """Complete receipt processing pipeline"""

    # Step 1: Load image
    original = load_image(image_path)

    # Step 2: Preprocess
    preprocessed = preprocess_image(original)

    # Step 3: Detect edges
    edges = detect_edges(preprocessed)

    # Step 4: Find receipt contour
    receipt_contour = find_receipt_contour(edges)

    if receipt_contour is None:
        print("Could not find receipt in image")
        return None

    # Step 5: Apply perspective transformation (deskew)
    warped = four_point_transform(original, receipt_contour.reshape(4, 2))

    # Step 6: Remove background and cleanup
    final = remove_background(warped)

    # Step 7: Save if output path provided
    if output_path:
        cv2.imwrite(output_path, final)

    return final
```

## Web Application Architecture

### Recommended Framework: **FastAPI**

FastAPI is ideal for this application because:
- **Async support** for handling multiple uploads
- **Fast performance**
- **Automatic API documentation**
- **Easy file upload handling**
- **Type safety**

### Basic API Structure

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from typing import List

app = FastAPI(title="Receipt Scanner API")

@app.post("/scan-receipt/")
async def scan_receipt(file: UploadFile = File(...)):
    """
    Upload receipt image for processing
    Returns: Processed image and extracted text
    """
    try:
        # Read uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Process receipt
        processed = process_receipt_from_array(image)

        # Extract text
        text = extract_text_paddleocr(processed)

        # Return results
        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "extracted_text": text
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

## Project Structure

```
receipts/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   └── routes/
│   │       └── scan.py          # Scan endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_processor.py  # Image preprocessing
│   │   ├── receipt_detector.py # Receipt detection
│   │   ├── ocr_service.py      # OCR integration
│   │   └── deskew_service.py   # Deskewing logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── receipt.py          # Receipt data model
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_utils.py      # Image helper functions
│   │   └── validation.py       # Input validation
│   └── config/
│       └── settings.py          # Configuration
├── models/
│   └── yolo/
│       └── receipt_detector.pt  # Trained YOLO model
├── tests/
│   ├── test_image_processor.py
│   ├── test_ocr_service.py
│   └── fixtures/
│       └── sample_receipts/     # Test images
├── requirements.txt
├── Dockerfile
└── README.md
```

## Dependencies (requirements.txt)

```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Image Processing
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.1.0

# OCR (choose one or multiple)
paddlepaddle==2.5.1
paddleocr==2.7.0.3

# Alternative OCR
pytesseract==0.3.10
python-doctr==0.7.0

# ML/Detection
ultralytics==8.0.220  # YOLOv8
torch==2.1.0
torchvision==0.16.0

# Utilities
pydantic==2.5.0
python-jose==3.3.0
```

## Implementation Phases

### Phase 1: Basic Image Processing (Week 1-2)
- [ ] Set up Python environment
- [ ] Implement image loading and preprocessing
- [ ] Implement edge detection and contour finding
- [ ] Implement perspective transformation (deskewing)
- [ ] Test with sample receipts

### Phase 2: Background Removal & Cleanup (Week 2-3)
- [ ] Implement adaptive thresholding
- [ ] Add morphological operations
- [ ] Test background removal on various receipt types
- [ ] Handle edge cases (crumpled receipts, shadows)

### Phase 3: OCR Integration (Week 3-4)
- [ ] Integrate PaddleOCR
- [ ] Test OCR accuracy
- [ ] Implement text post-processing
- [ ] Extract structured data (merchant, date, total, items)

### Phase 4: ML-Enhanced Detection (Week 4-5)
- [ ] Train or fine-tune YOLO model for receipt detection
- [ ] Integrate YOLO for robust receipt boundary detection
- [ ] Compare results with contour-based approach
- [ ] Implement fallback logic

### Phase 5: Web API Development (Week 5-6)
- [ ] Set up FastAPI application
- [ ] Implement file upload endpoint
- [ ] Add processing queue for async handling
- [ ] Implement result storage and retrieval
- [ ] Add error handling and validation

### Phase 6: Frontend Development (Week 6-7)
- [ ] Create image upload interface
- [ ] Add real-time preview
- [ ] Display processed results
- [ ] Implement image editing tools (manual adjustment)

### Phase 7: Testing & Optimization (Week 7-8)
- [ ] Unit tests for all components
- [ ] Integration tests for pipeline
- [ ] Performance optimization
- [ ] Load testing
- [ ] Deploy to staging environment

## Performance Considerations

### Optimization Strategies

1. **Image Resizing**
   - Resize large images before processing
   - Maintain aspect ratio
   - Target: 1500px max dimension

2. **Async Processing**
   - Use background tasks for heavy processing
   - Implement job queue (Celery, RQ)
   - Return job ID immediately, poll for results

3. **Caching**
   - Cache processed results
   - Use Redis for temporary storage
   - Implement TTL for cleanup

4. **Model Optimization**
   - Use quantized models for faster inference
   - Consider ONNX runtime for deployment
   - GPU acceleration for ML models

## Error Handling

### Common Issues and Solutions

1. **Receipt Not Found**
   - Fallback to YOLO detection
   - Prompt user for manual selection
   - Return original image with warning

2. **Skewed Detection Failure**
   - Use rotation angle detection
   - Try multiple edge detection thresholds
   - Implement manual adjustment interface

3. **Poor OCR Results**
   - Try multiple OCR engines
   - Apply additional preprocessing
   - Increase image resolution
   - User correction interface

4. **Large File Uploads**
   - Implement file size limits (10MB recommended)
   - Client-side image compression
   - Stream processing for large files

## Security Considerations

1. **File Upload Validation**
   - Check file type (JPEG, PNG only)
   - Scan for malicious content
   - Limit file size
   - Validate image integrity

2. **Data Privacy**
   - Delete uploaded images after processing
   - Encrypt stored receipt data
   - Implement user authentication
   - GDPR compliance for EU users

3. **Rate Limiting**
   - Limit requests per user/IP
   - Prevent abuse and DoS
   - Implement CAPTCHA for anonymous users

## Testing Strategy

### Test Cases

1. **Perfect Conditions**
   - Clean, well-lit receipt on white background
   - No skew, no shadows
   - Expected: 100% accurate detection and cropping

2. **Skewed Receipts**
   - Receipt at various angles (15°, 30°, 45°)
   - Expected: Automatic deskewing and correction

3. **Complex Backgrounds**
   - Receipt on table with items
   - Receipt on patterned surface
   - Expected: Accurate receipt isolation

4. **Poor Lighting**
   - Shadows on receipt
   - Low light conditions
   - Expected: Preprocessing handles shadows

5. **Damaged Receipts**
   - Crumpled or folded
   - Torn edges
   - Expected: Graceful degradation or error message

## Future Enhancements

1. **Mobile App**
   - Native iOS/Android apps
   - Real-time camera processing
   - Offline processing capability

2. **Batch Processing**
   - Upload multiple receipts at once
   - Automatic categorization
   - Bulk export

3. **AI-Powered Insights**
   - Spending analytics
   - Merchant recognition
   - Category auto-tagging
   - Duplicate detection

4. **Integration Options**
   - Accounting software (QuickBooks, Xero)
   - Expense management tools
   - Cloud storage (Google Drive, Dropbox)

## Resources

### Tutorials
- [OpenCV Receipt Scanner Tutorial](https://pyimagesearch.com/2014/09/01/build-kick-ass-mobile-document-scanner-just-5-minutes/)
- [Document Scanning with Python](https://www.pyimagesearch.com/2020/08/31/camera-calibration-with-opencv/)

### Documentation
- [OpenCV Python Docs](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Sample Datasets
- [SROIE Dataset](https://rrc.cvc.uab.es/?ch=13) - Scanned Receipt OCR and Information Extraction
- [CORD Dataset](https://github.com/clovaai/cord) - Consolidated Receipt Dataset

## Contact & Questions

For implementation questions or technical support, refer to:
- **CLAUDE.md** - AI assistant development guidelines
- **README.md** - General project information
- Project issue tracker

---

**Last Updated:** 2025-11-27
**Next Review:** After Phase 1 completion
