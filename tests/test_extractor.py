import pytest
from unittest.mock import MagicMock, patch
from src.services.pdf_extractor import PDFExtractor


def test_extract_returns_dict_on_success():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"vendor": "Anthropic", "invoice_date": "2025-08-01", "amount_aud": 50.00, "ato_category": "Software & Subscriptions", "description": "API usage"}')]

    with patch("anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = mock_response
        extractor = PDFExtractor(api_key="test")
        result = extractor.extract(b"%PDF-fake")

    assert result["vendor"] == "Anthropic"
    assert result["amount_aud"] == 50.00


def test_extract_returns_empty_dict_on_failure():
    with patch("anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.side_effect = Exception("API error")
        extractor = PDFExtractor(api_key="test")
        result = extractor.extract(b"%PDF-fake")

    assert result == {}
