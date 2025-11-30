"""OCR service for extracting text from receipt images."""

import numpy as np
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from src.config.settings import settings


class OCRService:
    """Service for extracting text from receipt images using PaddleOCR."""

    def __init__(self, language: str = None, use_angle_cls: bool = None):
        """
        Initialize OCR service.

        Args:
            language: Language code (default from settings)
            use_angle_cls: Whether to use angle classification (default from settings)
        """
        self.language = language or settings.ocr_language
        self.use_angle_cls = use_angle_cls if use_angle_cls is not None else settings.ocr_use_angle_cls
        self._ocr_engine = None

    def _initialize_ocr(self):
        """Lazy initialization of PaddleOCR engine."""
        if self._ocr_engine is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr_engine = PaddleOCR(
                    use_angle_cls=self.use_angle_cls,
                    lang=self.language
                )
            except ImportError:
                raise ImportError(
                    "PaddleOCR is not installed. "
                    "Install it with: pip install paddlepaddle paddleocr"
                )

    def extract_text(
        self,
        image: Union[str, Path, np.ndarray],
        return_confidence: bool = False
    ) -> Union[List[str], List[Dict[str, Any]]]:
        """
        Extract text from image.

        Args:
            image: Image file path or numpy array
            return_confidence: If True, return confidence scores with text

        Returns:
            List of text lines, or list of dicts with text and confidence

        Example:
            >>> ocr = OCRService()
            >>> text_lines = ocr.extract_text("receipt.jpg")
            >>> print(text_lines)
            ['STORE NAME', 'Item 1: $10.00', 'Total: $10.00']
        """
        self._initialize_ocr()

        # Convert Path to string
        if isinstance(image, Path):
            image = str(image)

        try:
            # Perform OCR
            result = self._ocr_engine.ocr(image, cls=self.use_angle_cls)

            if result is None or len(result) == 0 or result[0] is None:
                return []

            # Extract text and optionally confidence
            text_results = []
            for line in result[0]:
                text = line[1][0]  # Text content
                confidence = line[1][1]  # Confidence score

                if return_confidence:
                    text_results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': line[0]  # Bounding box coordinates
                    })
                else:
                    text_results.append(text)

            return text_results

        except Exception as e:
            raise RuntimeError(f"OCR extraction failed: {str(e)}")

    def extract_structured_data(
        self,
        image: Union[str, Path, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Extract structured data from receipt.

        This method attempts to extract common receipt fields like
        merchant name, total, date, etc.

        Args:
            image: Image file path or numpy array

        Returns:
            Dictionary with extracted fields

        Example:
            >>> ocr = OCRService()
            >>> data = ocr.extract_structured_data("receipt.jpg")
            >>> print(data['total'])
            10.00
        """
        # Extract all text with confidence
        text_results = self.extract_text(image, return_confidence=True)

        if not text_results:
            return {
                'raw_text': [],
                'merchant': None,
                'date': None,
                'total': None,
                'items': []
            }

        # Extract raw text
        raw_text = [item['text'] for item in text_results]

        # Simple heuristics for extracting structured data
        # In production, you'd use more sophisticated parsing
        structured = {
            'raw_text': raw_text,
            'merchant': self._extract_merchant(text_results),
            'date': self._extract_date(text_results),
            'total': self._extract_total(text_results),
            'items': self._extract_items(text_results)
        }

        return structured

    def _extract_merchant(self, text_results: List[Dict[str, Any]]) -> Optional[str]:
        """Extract merchant name (typically first line with high confidence)."""
        if not text_results:
            return None

        # First line is often the merchant name
        first_line = text_results[0]
        if first_line['confidence'] > 0.8:
            return first_line['text']

        return None

    def _extract_date(self, text_results: List[Dict[str, Any]]) -> Optional[str]:
        """Extract date from receipt."""
        import re

        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}',         # YYYY-MM-DD
            r'\d{1,2}-\d{1,2}-\d{2,4}'    # MM-DD-YYYY or DD-MM-YYYY
        ]

        for item in text_results:
            text = item['text']
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(0)

        return None

    def _extract_total(self, text_results: List[Dict[str, Any]]) -> Optional[float]:
        """Extract total amount from receipt."""
        import re

        # Look for "TOTAL" followed by amount (not subtotal)
        total_keywords = ['total']
        exclude_keywords = ['subtotal', 'sub total']

        for i, item in enumerate(text_results):
            text_lower = item['text'].lower()

            # Skip if it's subtotal
            if any(exclude in text_lower for exclude in exclude_keywords):
                continue

            # Check if line contains total keyword
            if any(keyword in text_lower for keyword in total_keywords):
                # Extract amount from this line or next line
                amount = self._extract_amount(item['text'])
                if amount is not None:
                    return amount

                # Check next line
                if i + 1 < len(text_results):
                    amount = self._extract_amount(text_results[i + 1]['text'])
                    if amount is not None:
                        return amount

        # Fallback: find largest amount
        amounts = []
        for item in text_results:
            amount = self._extract_amount(item['text'])
            if amount is not None:
                amounts.append(amount)

        return max(amounts) if amounts else None

    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from text."""
        import re

        # Pattern for currency amounts (try most specific first)
        patterns = [
            r'\$\s*([\d,]+\.\d{2})',      # $1,234.56 or $10.00
            r'([\d,]+\.\d{2})',           # 1,234.56 or 10.00
            r'\$\s*([\d,]+)',             # $1,234 or $10
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    return float(amount_str)
                except ValueError:
                    continue

        return None

    def _extract_items(self, text_results: List[Dict[str, Any]]) -> List[str]:
        """Extract line items from receipt."""
        # Simple implementation: return lines that contain amounts
        # but are not the total
        items = []

        for item in text_results:
            text = item['text']
            text_lower = text.lower()

            # Skip total line
            if 'total' in text_lower:
                continue

            # Check if line contains an amount
            if self._extract_amount(text) is not None:
                items.append(text)

        return items


class MockOCRService(OCRService):
    """Mock OCR service for testing without PaddleOCR dependency."""

    def __init__(self, language: str = "en", use_angle_cls: bool = True):
        """Initialize mock OCR service."""
        super().__init__(language, use_angle_cls)
        self._mock_results = []

    def set_mock_results(self, results: List[str]):
        """Set mock OCR results for testing."""
        self._mock_results = results

    def _initialize_ocr(self):
        """Skip PaddleOCR initialization for mock."""
        pass

    def extract_text(
        self,
        image: Union[str, Path, np.ndarray],
        return_confidence: bool = False
    ) -> Union[List[str], List[Dict[str, Any]]]:
        """Return mock text results."""
        if not self._mock_results:
            return []

        if return_confidence:
            return [
                {
                    'text': text,
                    'confidence': 0.95,
                    'bbox': [[0, 0], [100, 0], [100, 20], [0, 20]]
                }
                for text in self._mock_results
            ]
        else:
            return self._mock_results.copy()
