"""API routes for receipt scanning."""

import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from typing import Optional
import tempfile
import base64

from src.services.image_processor import ReceiptProcessor
from src.services.ocr_service import OCRService
from src.config.settings import settings

router = APIRouter()


@router.post("/scan")
async def scan_receipt(
    file: UploadFile = File(...),
    extract_text: bool = Query(False, description="Extract text using OCR"),
    return_image: bool = Query(False, description="Return processed image as base64"),
    min_area_percent: float = Query(5.0, description="Minimum receipt area as % of image (use 0.01 for small receipts)"),
    approx_tolerance: float = Query(0.02, description="Contour approximation tolerance (increase for complex edges)")
):
    """
    Scan and process a receipt image.

    This endpoint:
    1. Removes borders and background
    2. Fixes skewness (deskewing)
    3. Crops to receipt boundaries
    4. Optionally extracts text using OCR

    Args:
        file: Receipt image file (JPEG, PNG)
        extract_text: Whether to extract text using OCR
        return_image: Whether to return processed image as base64
        min_area_percent: Minimum receipt area (default 5.0%, use 0.01 for small receipts)
        approx_tolerance: Contour approximation (default 0.02, higher = more lenient)

    Returns:
        JSON with processing results

    Example:
        ```bash
        # Standard processing
        curl -X POST "http://localhost:8000/api/v1/scan?extract_text=true" \\
             -F "file=@receipt.jpg"

        # For small receipts in large photos
        curl -X POST "http://localhost:8000/api/v1/scan?min_area_percent=0.01" \\
             -F "file=@receipt.jpg"
        ```
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG)"
        )

    try:
        # Read uploaded file
        contents = await file.read()

        # Validate file size
        if len(contents) > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )

        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

        # Process receipt
        processor = ReceiptProcessor()
        result = processor.process_receipt(
            image,
            min_area_percent=min_area_percent,
            approx_tolerance=approx_tolerance
        )

        if not result['success']:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": result['message'],
                    "filename": file.filename
                }
            )

        # Prepare response
        response_data = {
            "success": True,
            "message": "Receipt processed successfully",
            "filename": file.filename
        }

        # Add processed image as base64 if requested
        if return_image and result['processed_image'] is not None:
            _, buffer = cv2.imencode('.jpg', result['processed_image'])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            response_data['processed_image'] = img_base64

        # Extract text if requested
        if extract_text and result['processed_image'] is not None:
            try:
                ocr = OCRService()
                structured_data = ocr.extract_structured_data(result['processed_image'])
                response_data['ocr'] = structured_data
            except Exception as e:
                response_data['ocr_error'] = f"OCR failed: {str(e)}"

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing receipt: {str(e)}"
        )


@router.post("/scan/save")
async def scan_and_save_receipt(
    file: UploadFile = File(...),
    extract_text: bool = Query(False, description="Extract text using OCR"),
    min_area_percent: float = Query(5.0, description="Minimum receipt area as % of image (use 0.01 for small receipts)"),
    approx_tolerance: float = Query(0.02, description="Contour approximation tolerance")
):
    """
    Scan receipt and save processed image.

    Returns a downloadable processed receipt image.

    Args:
        file: Receipt image file
        extract_text: Whether to extract text using OCR
        min_area_percent: Minimum receipt area (default 5.0%, use 0.01 for small receipts)
        approx_tolerance: Contour approximation (default 0.02)

    Returns:
        Processed image file or JSON with OCR results
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    try:
        # Read uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

        # Process receipt
        processor = ReceiptProcessor()

        # Create temp file for output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            output_path = tmp_file.name

        result = processor.process_receipt(
            image,
            output_path=output_path,
            min_area_percent=min_area_percent,
            approx_tolerance=approx_tolerance
        )

        if not result['success']:
            Path(output_path).unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=result['message']
            )

        # If OCR requested, return JSON instead of image
        if extract_text:
            try:
                ocr = OCRService()
                structured_data = ocr.extract_structured_data(result['processed_image'])

                # Cleanup temp file
                Path(output_path).unlink(missing_ok=True)

                return JSONResponse(content={
                    "success": True,
                    "filename": file.filename,
                    "ocr": structured_data
                })
            except Exception as e:
                Path(output_path).unlink(missing_ok=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"OCR failed: {str(e)}"
                )

        # Return processed image file
        return FileResponse(
            output_path,
            media_type="image/jpeg",
            filename=f"processed_{file.filename}",
            background=None  # File will be kept until download completes
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing receipt: {str(e)}"
        )


@router.post("/visualize")
async def visualize_detection(
    file: UploadFile = File(...),
    min_area_percent: float = Query(5.0, description="Minimum receipt area as % of image (use 0.01 for small receipts)"),
    approx_tolerance: float = Query(0.02, description="Contour approximation tolerance")
):
    """
    Visualize receipt detection.

    Returns the original image with detected receipt boundaries drawn.

    Args:
        file: Receipt image file
        min_area_percent: Minimum receipt area (default 5.0%, use 0.01 for small receipts)
        approx_tolerance: Contour approximation (default 0.02)

    Returns:
        Image with detection visualization
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    try:
        # Read uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

        # Create visualization
        processor = ReceiptProcessor()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            output_path = tmp_file.name

        vis_image = processor.visualize_detection(
            image,
            output_path,
            min_area_percent=min_area_percent,
            approx_tolerance=approx_tolerance
        )

        if vis_image is None:
            Path(output_path).unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail="Could not detect receipt in image. Try min_area_percent=0.01 for small receipts."
            )

        return FileResponse(
            output_path,
            media_type="image/jpeg",
            filename=f"visualization_{file.filename}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating visualization: {str(e)}"
        )


@router.post("/extract")
async def extract_receipt_data(
    file: UploadFile = File(...)
):
    """
    Extract structured data from receipt image to JSON.

    Works with any receipt image - no perfect detection needed.
    Returns merchant, date, items, totals, payment info as JSON.

    Args:
        file: Receipt image file

    Returns:
        JSON with structured receipt data

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/extract" \\
             -F "file=@receipt.jpg"
        ```
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    try:
        # Read uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

        # Extract data with OCR
        try:
            # Save image to temp file for PaddleOCR
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                cv2.imwrite(tmp.name, image)
                temp_path = tmp.name

            try:
                ocr = OCRService()
                data = ocr.extract_structured_data(temp_path)

                # Add metadata
                data['_metadata'] = {
                    'filename': file.filename,
                    'image_size': f"{image.shape[1]}x{image.shape[0]}"
                }

                return JSONResponse(
                    status_code=200,
                    content=data
                )
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        except Exception as ocr_error:
            import traceback
            error_details = traceback.format_exc()
            raise HTTPException(
                status_code=500,
                detail=f"OCR extraction failed: {str(ocr_error)}\nDetails: {error_details}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing receipt: {str(e)}"
        )


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working."""
    return {
        "status": "ok",
        "message": "Scan API is operational",
        "endpoints": {
            "scan": "/api/v1/scan",
            "scan_and_save": "/api/v1/scan/save",
            "visualize": "/api/v1/visualize",
            "extract": "/api/v1/extract"
        }
    }
