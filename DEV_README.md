# Receipt Scanner - Developer Guide

## Quick Start

### Installation

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test file:
```bash
pytest tests/unit/utils/test_image_utils.py
```

Run tests by marker:
```bash
pytest -m unit
```

### Running the API

Start the development server:
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or run directly:
```bash
python -m src.api.main
```

API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Using the API

#### 1. Basic Receipt Scanning

```bash
curl -X POST "http://localhost:8000/api/v1/scan" \
  -F "file=@receipt.jpg"
```

#### 2. Scan with OCR

```bash
curl -X POST "http://localhost:8000/api/v1/scan?extract_text=true" \
  -F "file=@receipt.jpg"
```

#### 3. Scan and Save Processed Image

```bash
curl -X POST "http://localhost:8000/api/v1/scan/save" \
  -F "file=@receipt.jpg" \
  --output processed_receipt.jpg
```

#### 4. Visualize Detection

```bash
curl -X POST "http://localhost:8000/api/v1/visualize" \
  -F "file=@receipt.jpg" \
  --output visualization.jpg
```

## Project Structure

```
receipts/
├── src/                          # Source code
│   ├── api/                     # FastAPI application
│   │   ├── main.py             # Main app entry point
│   │   └── routes/
│   │       └── scan.py         # Scan endpoints
│   ├── services/               # Business logic
│   │   ├── image_processor.py  # Main processing pipeline
│   │   ├── receipt_detector.py # Receipt detection
│   │   └── ocr_service.py      # OCR integration
│   ├── utils/                  # Utility functions
│   │   └── image_utils.py      # Image processing helpers
│   └── config/                 # Configuration
│       └── settings.py         # App settings
├── tests/                       # Tests
│   ├── conftest.py             # Test fixtures
│   └── unit/                   # Unit tests
│       ├── api/
│       ├── services/
│       └── utils/
├── requirements.txt            # Dependencies
├── pytest.ini                  # Pytest configuration
└── RECEIPT_SCANNING.md        # Implementation guide
```

## Code Examples

### Using the Receipt Processor Directly

```python
from src.services.image_processor import ReceiptProcessor

# Initialize processor
processor = ReceiptProcessor()

# Process receipt
result = processor.process_receipt(
    "receipt.jpg",
    output_path="processed.jpg",
    return_steps=True
)

if result['success']:
    print("Receipt processed!")
    print(f"Message: {result['message']}")

    # Access intermediate steps
    if result['steps']:
        for step_name, step_image in result['steps'].items():
            print(f"Step {step_name}: {step_image.shape}")
else:
    print(f"Failed: {result['message']}")
```

### Using OCR Service

```python
from src.services.ocr_service import OCRService

# Initialize OCR
ocr = OCRService()

# Extract text
text_lines = ocr.extract_text("receipt.jpg")
print("Text lines:", text_lines)

# Extract structured data
data = ocr.extract_structured_data("receipt.jpg")
print(f"Merchant: {data['merchant']}")
print(f"Total: ${data['total']}")
print(f"Date: {data['date']}")
print(f"Items: {data['items']}")
```

### Simple Receipt Processing

```python
from src.services.image_processor import process_receipt_simple

# One-line processing
processed = process_receipt_simple("receipt.jpg", "output.jpg")

if processed is not None:
    print("Success!")
else:
    print("Failed to process receipt")
```

## Configuration

Edit `src/config/settings.py` or use environment variables:

```bash
# .env file
MAX_IMAGE_DIMENSION=1500
MAX_FILE_SIZE_MB=10
CANNY_THRESHOLD1=75
CANNY_THRESHOLD2=200
OCR_LANGUAGE=en
```

## Testing

### Test Structure

- **Unit tests**: Test individual functions
- **Integration tests**: Test complete workflows
- **Fixtures**: Reusable test data in `conftest.py`

### Writing Tests

```python
import pytest
from src.utils.image_utils import load_image

class TestLoadImage:
    @pytest.mark.unit
    def test_load_image_success(self, sample_image):
        """Test loading a valid image."""
        result = load_image(sample_image)
        assert result is not None
```

### Test Coverage

View coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # On Mac/Linux
```

## Common Issues

### PaddleOCR Installation

If PaddleOCR installation fails:

```bash
# Install PaddlePaddle first
pip install paddlepaddle

# Then install PaddleOCR
pip install paddleocr
```

For CPU-only:
```bash
pip install paddlepaddle
```

For GPU (CUDA 11.x):
```bash
pip install paddlepaddle-gpu
```

### OpenCV Issues

If cv2 import fails:
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

## Performance Tips

1. **Image Resizing**: Large images are automatically resized to MAX_IMAGE_DIMENSION
2. **Caching**: Consider caching processed results for frequently accessed receipts
3. **Async Processing**: Use background tasks for heavy OCR processing
4. **GPU Acceleration**: Use PaddlePaddle GPU version for faster OCR

## API Response Examples

### Successful Scan

```json
{
  "success": true,
  "message": "Receipt processed successfully",
  "filename": "receipt.jpg"
}
```

### Scan with OCR

```json
{
  "success": true,
  "message": "Receipt processed successfully",
  "filename": "receipt.jpg",
  "ocr": {
    "raw_text": ["WALMART", "Item 1: $10.00", "Total: $10.00"],
    "merchant": "WALMART",
    "date": "11/27/2024",
    "total": 10.00,
    "items": ["Item 1: $10.00"]
  }
}
```

### Failed Detection

```json
{
  "success": false,
  "message": "Could not detect receipt in image",
  "filename": "photo.jpg"
}
```

## Development Workflow

1. **Make changes** to source code
2. **Write tests** for new functionality
3. **Run tests** to verify: `pytest`
4. **Check coverage**: `pytest --cov=src`
5. **Test API** manually or with curl
6. **Commit** changes with clear message

## Next Steps

- [ ] Add batch processing endpoint
- [ ] Implement caching layer
- [ ] Add user authentication
- [ ] Create frontend interface
- [ ] Deploy to production
- [ ] Add monitoring and logging
- [ ] Optimize OCR performance
- [ ] Train custom YOLO model for receipt detection

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **PaddleOCR**: https://github.com/PaddlePaddle/PaddleOCR
- **OpenCV Python**: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- **pytest**: https://docs.pytest.org/

## Support

For issues or questions:
1. Check RECEIPT_SCANNING.md for implementation details
2. Check CLAUDE.md for development guidelines
3. Run tests to verify setup: `pytest`
4. Check API docs: http://localhost:8000/docs
