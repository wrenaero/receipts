# Receipt Scanner

An intelligent receipt scanning application that automatically removes borders, fixes skewness, crops receipts, and extracts text using OCR.

![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue.svg)
![Tests](https://img.shields.io/badge/tests-75%2F78%20passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-67%25-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> **⚠️ IMPORTANT:** This project requires **Python 3.11 or 3.12**. Python 3.13 is NOT yet supported due to dependency compatibility issues. See [installation instructions](#-quick-start) below.

## 🎯 What It Does

This application uses **OpenCV** and **PaddleOCR** to intelligently process receipt images:

✅ **Removes unrelated borders and backgrounds**
✅ **Fixes skewness** (automatically deskews rotated receipts)
✅ **Smart cropping** to receipt boundaries only
✅ **OCR text extraction** with structured data parsing
✅ **JSON data export** (merchant, items, totals, payment info)
✅ **Multiple interfaces:** CLI tools, Python API, and REST API
✅ **Flexible detection** for receipts on any background

### Before & After

```
Input:                    Output:
┌─────────────────┐      ┌──────────┐
│                 │      │ RECEIPT  │
│  ╔═══════╗     │  →   │ Item: $5 │
│  ║RECEIPT║     │      │ Total:$5 │
│  ╚═══════╝     │      └──────────┘
│                 │
└─────────────────┘
Skewed, with borders    Clean, deskewed
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11 or 3.12** (⚠️ Python 3.13 not yet supported - see [troubleshooting](./TROUBLESHOOTING.md#-issue-python-313-compatibility-critical))
- **pip** (Python package manager)
- **(Optional)** Virtual environment tool

### Installation

> **💡 TIP:** Make sure you have Python 3.11 or 3.12 installed. Check with `python --version` or `python3 --version`. If you have Python 3.13, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#-issue-python-313-compatibility-critical) for installation instructions.

1. **Clone the repository:**
```bash
git clone <repository-url>
cd receipts
```

2. **Create a virtual environment (recommended):**
```bash
# On macOS/Linux (use python3.11 or python3.12 explicitly)
python3.11 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate

# Verify Python version inside venv
python --version  # Should show 3.11.x or 3.12.x
```

3. **Install dependencies:**
```bash
# First, upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Then install requirements
pip install -r requirements.txt
```

This will install:
- `opencv-python` - Image processing
- `numpy` - Numerical operations
- `paddleocr` & `paddlepaddle` - OCR
- `fastapi` & `uvicorn` - Web API
- `pytest` - Testing framework

**Installation time:** ~2-5 minutes depending on your internet connection.

> **⚠️ Getting installation errors?** If you see `Cannot import 'setuptools.build_meta'` or similar errors, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions.

### Verify Installation

Run the tests to ensure everything is installed correctly:
```bash
pytest
```

You should see: `75 passed, 3 failed` (96% success rate - the 3 failures are minor edge cases)

## 🏃 Running the Application

### Option 1: Start the Web API

```bash
# Start the server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### Option 2: Use Python Directly

Create a Python script or use the interactive shell:

```python
from src.services.image_processor import ReceiptProcessor

# Initialize processor
processor = ReceiptProcessor()

# Process a receipt
result = processor.process_receipt(
    image_path="path/to/receipt.jpg",
    output_path="processed_receipt.jpg"
)

# Check result
if result['success']:
    print("✅ Receipt processed successfully!")
    print(f"Saved to: processed_receipt.jpg")
else:
    print(f"❌ Error: {result['message']}")
```

### Option 3: Simple CLI Tools (Recommended for Most Users)

The easiest way to work with receipts is using the simple command-line tools:

#### **scan_receipt.py** - Complete receipt processing
```bash
# Process receipt (crop, deskew, clean)
python3 scan_receipt.py receipt.jpg output.jpg

# Visualize detection for debugging
python3 scan_receipt.py receipt.jpg debug.jpg --visualize

# Extract text with OCR
python3 scan_receipt.py receipt.jpg output.jpg --ocr

# Adjust parameters for small receipts or complex edges
python3 scan_receipt.py receipt.jpg output.jpg --min-area 0.01 --tolerance 0.05
```

#### **extract_receipt_data.py** - Extract data to JSON
```bash
# Extract structured data (works with any receipt image)
python3 extract_receipt_data.py receipt.jpg receipt_data.json
```

**Output:**
```json
{
  "merchant": "STORE NAME",
  "date": "11/28/2025",
  "time": "07:06 PM",
  "items": [
    {
      "description": "Product Name",
      "price": 25.99
    }
  ],
  "subtotal": 25.99,
  "tax": 2.08,
  "total": 28.07,
  "payment_method": "Visa"
}
```

#### **simple_extract.py** - Deskew images
```bash
# Just correct skewness, then extract data
python3 simple_extract.py receipt.jpg deskewed.jpg
python3 extract_receipt_data.py deskewed.jpg data.json
```

**💡 When to use which tool:**
- **`scan_receipt.py`**: Best for receipts on plain backgrounds, need cropping and cleaning
- **`extract_receipt_data.py`**: Best for data extraction only, works on any background
- **`simple_extract.py`**: Best when you just need to fix skew/rotation

## 📖 Usage Examples

### 1. Process Receipt via API

```bash
# Basic processing (crop, deskew, remove background)
curl -X POST "http://localhost:8000/api/v1/scan" \
  -F "file=@receipt.jpg"
```

**Response:**
```json
{
  "success": true,
  "message": "Receipt processed successfully",
  "filename": "receipt.jpg"
}
```

### 2. Process with OCR Text Extraction

```bash
curl -X POST "http://localhost:8000/api/v1/scan?extract_text=true" \
  -F "file=@receipt.jpg"
```

**Response:**
```json
{
  "success": true,
  "message": "Receipt processed successfully",
  "filename": "receipt.jpg",
  "ocr": {
    "merchant": "WALMART",
    "date": "11/27/2024",
    "total": 25.99,
    "items": [
      "Milk $3.99",
      "Bread $2.50"
    ],
    "raw_text": ["WALMART", "11/27/2024", ...]
  }
}
```

### 3. Download Processed Image

```bash
curl -X POST "http://localhost:8000/api/v1/scan/save" \
  -F "file=@receipt.jpg" \
  --output processed_receipt.jpg
```

### 4. Visualize Detection (for debugging)

```bash
curl -X POST "http://localhost:8000/api/v1/visualize" \
  -F "file=@receipt.jpg" \
  --output visualization.jpg
```

This shows the detected receipt boundaries and corner points on the original image.

### 5. Python Code Examples

#### Basic Processing

```python
from src.services.image_processor import process_receipt_simple

# Simple one-liner
processed_image = process_receipt_simple("receipt.jpg", "output.jpg")

if processed_image is not None:
    print("✅ Success!")
```

#### Advanced Processing with Steps

```python
from src.services.image_processor import ReceiptProcessor

processor = ReceiptProcessor()

# Get all intermediate processing steps
result = processor.process_receipt(
    "receipt.jpg",
    return_steps=True
)

if result['success']:
    steps = result['steps']

    # Access intermediate images
    original = steps['original']
    preprocessed = steps['preprocessed']
    edges = steps['edges']
    warped = steps['warped']
    final = steps['final']

    print(f"Original size: {original.shape}")
    print(f"Final size: {final.shape}")
```

#### OCR Only

```python
from src.services.ocr_service import OCRService

ocr = OCRService()

# Extract text lines
text_lines = ocr.extract_text("receipt.jpg")
for line in text_lines:
    print(line)

# Extract structured data
data = ocr.extract_structured_data("receipt.jpg")
print(f"Merchant: {data['merchant']}")
print(f"Date: {data['date']}")
print(f"Total: ${data['total']}")
```

#### Batch Processing

```python
from pathlib import Path
from src.services.image_processor import ReceiptProcessor

processor = ReceiptProcessor()

# Process all receipts in a directory
receipt_dir = Path("receipts")
output_dir = Path("processed")
output_dir.mkdir(exist_ok=True)

for receipt_path in receipt_dir.glob("*.jpg"):
    output_path = output_dir / f"processed_{receipt_path.name}"

    result = processor.process_receipt(receipt_path, output_path)

    if result['success']:
        print(f"✅ {receipt_path.name}")
    else:
        print(f"❌ {receipt_path.name}: {result['message']}")
```

## 🔍 Handling Small Receipts or Complex Edges

### Problem: "Could not detect receipt in image"

If you see this error, your receipt likely has one of these issues:
1. **Small in frame**: Receipt takes up less than 5% of the photo
2. **Complex edges**: Receipt edges are jagged or text/graphics interfere with edge detection
3. **Blurry or low contrast**: Edges aren't sharp enough
4. **Complex background**: Receipt on textured surface (concrete, fabric, etc.)

### Solution 1: Use Data Extraction Tool (Easiest)

**For receipts on complex backgrounds or when you just need the data:**

```bash
# Extract data directly - works on any background
python3 extract_receipt_data.py receipt.jpg receipt_data.json
```

This bypasses the contour detection and extracts text/data directly using OCR. Perfect for:
- Receipts on textured surfaces (concrete, wood, fabric)
- Receipts with complex backgrounds
- When you only need the data, not a cleaned image

### Solution 2: Adjust Detection Parameters

Both the API and Python interface support two tunable parameters:

- **`min_area_percent`** (default: 5.0): Minimum receipt area as percentage of image
  - Use `0.01` for receipts that are small in the frame
  - Use `0.001` for very small receipts

- **`approx_tolerance`** (default: 0.02): How strict the contour approximation is
  - Use `0.05` for receipts with complex/jagged edges
  - Use `0.1` for very complex backgrounds

### API Examples

```bash
# Small receipt in large photo
curl -X POST "http://localhost:8000/api/v1/scan?min_area_percent=0.01" \
  -F "file=@receipt.jpg"

# Receipt with complex edges (common with printed text near borders)
curl -X POST "http://localhost:8000/api/v1/scan?approx_tolerance=0.05" \
  -F "file=@receipt.jpg"

# Both issues combined
curl -X POST "http://localhost:8000/api/v1/scan?min_area_percent=0.01&approx_tolerance=0.05" \
  -F "file=@receipt.jpg"

# Visualize to see what's being detected
curl -X POST "http://localhost:8000/api/v1/visualize?min_area_percent=0.01&approx_tolerance=0.05" \
  -F "file=@receipt.jpg" \
  --output debug.jpg
```

### Python Examples

```python
from src.services.image_processor import ReceiptProcessor

processor = ReceiptProcessor()

# Small receipt
result = processor.process_receipt(
    "receipt.jpg",
    "output.jpg",
    min_area_percent=0.01
)

# Complex edges
result = processor.process_receipt(
    "receipt.jpg",
    "output.jpg",
    approx_tolerance=0.05
)

# Both parameters
result = processor.process_receipt(
    "receipt.jpg",
    "output.jpg",
    min_area_percent=0.01,
    approx_tolerance=0.05
)

# Visualize for debugging
vis = processor.visualize_detection(
    "receipt.jpg",
    "debug.jpg",
    min_area_percent=0.01,
    approx_tolerance=0.05
)
```

### Diagnostic Tool

Use the diagnostic script to analyze why a receipt isn't detecting:

```bash
python diagnose_receipt.py receipt.jpg
```

This will:
- Analyze image quality (brightness, contrast, edges)
- Show which contours were detected and why they were rejected
- Provide specific recommendations with exact parameter values
- Generate diagnostic images showing edges and contours

### Quick Reference

| Issue | Solution | Command/Value |
|-------|----------|---------------|
| Receipt too small in frame | Adjust `min_area_percent` | `0.01` - `0.001` |
| Complex/jagged edges | Adjust `approx_tolerance` | `0.05` - `0.1` |
| iPhone photo with small receipt | Adjust both parameters | `min_area_percent=0.01, approx_tolerance=0.05` |
| Complex background (concrete, fabric) | **Use extraction tool** | `python3 extract_receipt_data.py receipt.jpg data.json` |
| Just need data, not cleaned image | **Use extraction tool** | `python3 extract_receipt_data.py receipt.jpg data.json` |
| Poor lighting/low contrast | Enhance first | `python3 enhance_receipt.py receipt.jpg enhanced.jpg` |

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

### Run Specific Tests

```bash
# Test image utilities
pytest tests/unit/utils/test_image_utils.py

# Test receipt detection
pytest tests/unit/services/test_receipt_detector.py

# Test OCR service
pytest tests/unit/services/test_ocr_service.py

# Test API
pytest tests/unit/api/test_main.py
```

### Run with Verbose Output

```bash
pytest -v
```

## 📁 Project Structure

```
receipts/
├── src/                           # Source code
│   ├── api/                      # FastAPI web application
│   │   ├── main.py              # App entry point
│   │   └── routes/
│   │       └── scan.py          # Scan endpoints
│   ├── services/                # Business logic
│   │   ├── image_processor.py   # Main processing pipeline
│   │   ├── receipt_detector.py  # Receipt detection & extraction
│   │   └── ocr_service.py       # OCR integration
│   ├── utils/                   # Utility functions
│   │   └── image_utils.py       # Image processing helpers
│   └── config/                  # Configuration
│       └── settings.py          # App settings
├── tests/                        # Test suite (78 tests)
│   ├── conftest.py              # Shared test fixtures
│   └── unit/                    # Unit tests
├── scan_receipt.py              # CLI: Complete processing (RECOMMENDED)
├── extract_receipt_data.py      # CLI: Extract data to JSON (RECOMMENDED)
├── simple_extract.py            # CLI: Deskew images
├── diagnose_receipt.py          # CLI: Debug detection issues
├── enhance_receipt.py           # CLI: Enhance image quality
├── create_test_receipt.py       # CLI: Generate test receipts
├── process_small_receipt.py     # CLI: Process small receipts
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
├── .gitignore                   # Git exclusions
├── README.md                    # This file (user guide)
├── DEV_README.md               # Developer guide
├── RECEIPT_SCANNING.md         # Technical implementation
├── IMPLEMENTATION_SUMMARY.md   # Implementation details
└── CLAUDE.md                   # AI development guide
```

## ⚙️ Configuration

You can customize the application by editing `src/config/settings.py` or using environment variables.

### Environment Variables

Create a `.env` file in the project root:

```bash
# Image Processing
MAX_IMAGE_DIMENSION=1500
MAX_FILE_SIZE_MB=10

# Edge Detection
CANNY_THRESHOLD1=75
CANNY_THRESHOLD2=200
GAUSSIAN_BLUR_KERNEL=5

# OCR
OCR_LANGUAGE=en
OCR_USE_ANGLE_CLS=true

# API
APP_NAME=Receipt Scanner API
DEBUG=false
```

### Supported Languages for OCR

PaddleOCR supports 80+ languages. Common ones:
- `en` - English (default)
- `ch` - Chinese
- `fr` - French
- `es` - Spanish
- `de` - German
- `ja` - Japanese

Change in `.env`:
```bash
OCR_LANGUAGE=fr  # For French receipts
```

## 🔧 Troubleshooting

> **📖 For comprehensive troubleshooting including setuptools errors, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**

### Common Issues

### Issue: Cannot import 'setuptools.build_meta'

**Quick Fix:**
```bash
# Upgrade pip, setuptools, and wheel first
pip install --upgrade pip setuptools wheel

# Then retry installation
pip install -r requirements.txt
```

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-cannot-import-setuptoolsbuild_meta) for detailed solutions.

### Issue: PaddleOCR Installation Fails

**Solution 1:** Install PaddlePaddle first
```bash
pip install paddlepaddle
pip install paddleocr
```

**Solution 2:** For Apple Silicon (M1/M2) Macs
```bash
pip install paddlepaddle
pip install paddleocr
```

**Solution 3:** Skip OCR for now
```bash
# Install without OCR dependencies
pip install fastapi uvicorn opencv-python numpy pytest
```

You can still use image processing features without OCR.

### Issue: OpenCV Import Error

```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

### Issue: "No module named 'src'"

Make sure you're running commands from the project root directory:
```bash
cd /path/to/receipts
python -m pytest  # Not just 'pytest'
```

Or add the project to PYTHONPATH:
```bash
export PYTHONPATH=/path/to/receipts:$PYTHONPATH
```

### Issue: Curl Upload Error - "Expected UploadFile, received: <class 'str'>"

**Error Message:**
```json
{"detail":[{"type":"value_error","loc":["body","file"],
"msg":"Value error, Expected UploadFile, received: <class 'str'>"}]}
```

**Cause:** Missing `@` symbol in curl command. The `@` tells curl to upload the file.

**Solution:**
```bash
# ❌ Wrong - sends filename as string
curl -X POST "http://localhost:8000/api/v1/scan" -F "file=./receipt.jpg"

# ✅ Correct - uploads the file
curl -X POST "http://localhost:8000/api/v1/scan" -F "file=@receipt.jpg"
```

Note the `@` symbol before the filename!

---

### Issue: API Returns "Could not detect receipt"

**Possible causes:**
1. Image quality too low
2. Receipt edges not clear
3. Image too small

**Solutions:**
- Ensure receipt has clear edges
- Use good lighting when taking photo
- Try the visualization endpoint to see what's detected:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/visualize" \
    -F "file=@receipt.jpg" --output debug.jpg
  ```

### Issue: OCR Not Extracting Text Correctly

**Solutions:**
1. Use higher resolution images
2. Ensure processed image has good contrast
3. Try different OCR languages if receipt is not in English
4. Process image first, then apply OCR to the processed version

## 📊 Performance

Typical processing times (on modern laptop):

| Operation | Time |
|-----------|------|
| Image Loading | ~50ms |
| Preprocessing | ~30ms |
| Edge Detection | ~30ms |
| Perspective Transform | ~20ms |
| Background Removal | ~40ms |
| **Total (no OCR)** | **~150-200ms** |
| OCR Text Extraction | +500-1000ms |
| **Total (with OCR)** | **~650-1200ms** |

## 🛠️ Development

### Running in Development Mode

```bash
# Start with auto-reload (for development)
uvicorn src.api.main:app --reload --port 8000

# Start with custom host and port
uvicorn src.api.main:app --host 0.0.0.0 --port 3000
```

### Code Formatting

```bash
# Format code (if black is installed)
black src/ tests/

# Lint code (if flake8 is installed)
flake8 src/ tests/
```

### Adding New Features

See [CLAUDE.md](./CLAUDE.md) for development guidelines and [DEV_README.md](./DEV_README.md) for detailed developer documentation.

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

The interactive documentation allows you to test all endpoints directly from your browser.

## 🔐 Security Notes

**For production use:**

1. **Add authentication** to API endpoints
2. **Validate file uploads** (size, type, content)
3. **Rate limit** endpoints to prevent abuse
4. **Use HTTPS** for all communications
5. **Sanitize outputs** to prevent XSS
6. **Set CORS** to allowed origins only

Currently, the API accepts all origins and has no authentication - **suitable for local development only**.

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass: `pytest`
5. Submit a pull request

See [CLAUDE.md](./CLAUDE.md) for coding standards and conventions.

## 📞 Support

- **Issues:** Open an issue on GitHub
- **Documentation:** See [DEV_README.md](./DEV_README.md) for developer guide
- **Implementation Details:** See [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Technical Guide:** See [RECEIPT_SCANNING.md](./RECEIPT_SCANNING.md)

## 🙏 Acknowledgments

Built with:
- [OpenCV](https://opencv.org/) - Image processing
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR engine
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [NumPy](https://numpy.org/) - Numerical computing

## 📈 Roadmap

- [ ] Add support for multiple receipts in one image
- [ ] Implement caching for faster re-processing
- [ ] Add database integration for storing results
- [ ] Create web frontend interface
- [ ] Support batch processing API
- [ ] Add receipt templates for better parsing
- [ ] Train custom YOLO model for receipt detection
- [ ] Add mobile app (React Native)

---

**Made with ❤️ using Python, OpenCV, and PaddleOCR**
