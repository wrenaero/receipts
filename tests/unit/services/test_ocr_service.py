"""Unit tests for OCR service."""

import pytest
import numpy as np

from src.services.ocr_service import MockOCRService


class TestMockOCRService:
    """Tests for MockOCRService."""

    @pytest.mark.unit
    def test_mock_ocr_initialization(self):
        """Test mock OCR service initialization."""
        ocr = MockOCRService()

        assert ocr is not None
        assert ocr.language == "en"
        assert ocr.use_angle_cls is True

    @pytest.mark.unit
    def test_extract_text_simple(self):
        """Test extracting text with mock service."""
        ocr = MockOCRService()
        ocr.set_mock_results([
            "STORE NAME",
            "Item 1: $10.00",
            "Item 2: $15.00",
            "Total: $25.00"
        ])

        # Create dummy image
        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_text(dummy_image)

        assert len(result) == 4
        assert result[0] == "STORE NAME"
        assert result[3] == "Total: $25.00"

    @pytest.mark.unit
    def test_extract_text_with_confidence(self):
        """Test extracting text with confidence scores."""
        ocr = MockOCRService()
        ocr.set_mock_results(["Text line 1", "Text line 2"])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_text(dummy_image, return_confidence=True)

        assert len(result) == 2
        assert result[0]['text'] == "Text line 1"
        assert result[0]['confidence'] == 0.95
        assert 'bbox' in result[0]

    @pytest.mark.unit
    def test_extract_text_empty_result(self):
        """Test extraction with no results."""
        ocr = MockOCRService()
        ocr.set_mock_results([])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_text(dummy_image)

        assert result == []

    @pytest.mark.unit
    def test_extract_structured_data_simple(self):
        """Test extracting structured data."""
        ocr = MockOCRService()
        ocr.set_mock_results([
            "WALMART",
            "12/25/2024",
            "Milk $3.99",
            "Bread $2.50",
            "TOTAL $6.49"
        ])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_structured_data(dummy_image)

        assert result is not None
        assert 'raw_text' in result
        assert 'merchant' in result
        assert 'date' in result
        assert 'total' in result
        assert 'items' in result

        assert len(result['raw_text']) == 5

    @pytest.mark.unit
    def test_extract_merchant(self):
        """Test merchant extraction."""
        ocr = MockOCRService()
        ocr.set_mock_results([
            "TARGET STORE",
            "123 Main St",
            "Item: $10.00"
        ])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_structured_data(dummy_image)

        assert result['merchant'] == "TARGET STORE"

    @pytest.mark.unit
    def test_extract_date_various_formats(self):
        """Test date extraction with various formats."""
        test_cases = [
            (["Date: 12/25/2024"], "12/25/2024"),
            (["2024-12-25"], "2024-12-25"),
            (["Date 12-25-2024"], "12-25-2024"),
        ]

        for mock_results, expected_date in test_cases:
            ocr = MockOCRService()
            ocr.set_mock_results(mock_results)

            dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
            result = ocr.extract_structured_data(dummy_image)

            assert result['date'] == expected_date

    @pytest.mark.unit
    def test_extract_total_with_keyword(self):
        """Test total extraction when 'total' keyword is present."""
        ocr = MockOCRService()
        ocr.set_mock_results([
            "Item 1: $5.00",
            "Item 2: $3.50",
            "Total: $8.50"
        ])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_structured_data(dummy_image)

        assert result['total'] == 8.50

    @pytest.mark.unit
    def test_extract_total_various_formats(self):
        """Test total extraction with various amount formats."""
        test_cases = [
            (["TOTAL $10.00"], 10.00),
            (["Total: 25.99"], 25.99),
            (["Sum $1,234.56"], 1234.56),
        ]

        for mock_results, expected_total in test_cases:
            ocr = MockOCRService()
            ocr.set_mock_results(mock_results)

            dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
            result = ocr.extract_structured_data(dummy_image)

            assert result['total'] == expected_total

    @pytest.mark.unit
    def test_extract_items(self):
        """Test item extraction."""
        ocr = MockOCRService()
        ocr.set_mock_results([
            "GROCERY STORE",
            "Milk $3.99",
            "Bread $2.50",
            "Eggs $4.25",
            "TOTAL $10.74"
        ])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_structured_data(dummy_image)

        # Should extract items but not total line
        assert len(result['items']) == 3
        assert "Milk $3.99" in result['items']
        assert "Bread $2.50" in result['items']
        assert "Eggs $4.25" in result['items']

    @pytest.mark.unit
    def test_extract_amount_helper(self):
        """Test the _extract_amount helper method."""
        ocr = MockOCRService()

        test_cases = [
            ("$10.00", 10.00),
            ("Total: $25.99", 25.99),
            ("Amount 15.50", 15.50),
            ("$1,234.56", 1234.56),
            ("No amount here", None),
        ]

        for text, expected_amount in test_cases:
            result = ocr._extract_amount(text)
            assert result == expected_amount

    @pytest.mark.unit
    def test_extract_structured_data_empty(self):
        """Test structured extraction with no text."""
        ocr = MockOCRService()
        ocr.set_mock_results([])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_structured_data(dummy_image)

        assert result['raw_text'] == []
        assert result['merchant'] is None
        assert result['date'] is None
        assert result['total'] is None
        assert result['items'] == []

    @pytest.mark.unit
    def test_extract_structured_data_complex_receipt(self):
        """Test extraction from complex receipt."""
        ocr = MockOCRService()
        ocr.set_mock_results([
            "WHOLE FOODS MARKET",
            "123 Market Street",
            "San Francisco, CA 94102",
            "Date: 11/27/2024",
            "Time: 14:35:22",
            "",
            "Organic Bananas $2.99",
            "Almond Milk $4.50",
            "Whole Grain Bread $3.25",
            "Fresh Spinach $2.15",
            "",
            "Subtotal: $12.89",
            "Tax: $1.16",
            "TOTAL: $14.05",
            "",
            "Thank you for shopping!"
        ])

        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = ocr.extract_structured_data(dummy_image)

        # Verify extracted data
        assert result['merchant'] == "WHOLE FOODS MARKET"
        assert result['date'] == "11/27/2024"
        assert result['total'] == 14.05  # Should find the TOTAL
        assert len(result['items']) >= 3  # Should find multiple items

    @pytest.mark.unit
    def test_custom_language(self):
        """Test OCR service with custom language."""
        ocr = MockOCRService(language="fr")

        assert ocr.language == "fr"

    @pytest.mark.unit
    def test_angle_classification_option(self):
        """Test OCR service with angle classification disabled."""
        ocr = MockOCRService(use_angle_cls=False)

        assert ocr.use_angle_cls is False
