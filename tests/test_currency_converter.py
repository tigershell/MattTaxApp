import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def converter(app):
    with app.app_context():
        with patch("src.logic.currency_converter.RBAClient") as MockRBA:
            mock_rba = MagicMock()
            MockRBA.return_value = mock_rba
            from src.logic.currency_converter import CurrencyConverter
            conv = CurrencyConverter()
            conv._rba = mock_rba
            yield conv, mock_rba


def test_aud_passthrough(converter):
    """AUD amounts should pass through with rate=1, no API call made."""
    conv, mock_rba = converter
    amount = Decimal("99.00")
    aud, rate = conv.convert(amount, "AUD", datetime.date(2025, 10, 1))
    assert aud == Decimal("99.00")
    assert rate == Decimal("1")
    mock_rba.get_rate.assert_not_called()


def test_usd_conversion(converter):
    """USD amounts should be multiplied by the fetched rate."""
    conv, mock_rba = converter
    mock_rba.get_rate.return_value = Decimal("1.55")
    aud, rate = conv.convert(Decimal("100.00"), "USD", datetime.date(2025, 10, 1))
    assert aud == Decimal("155.00")
    assert rate == Decimal("1.55")
    mock_rba.get_rate.assert_called_once_with(datetime.date(2025, 10, 1), "USD")


def test_usd_conversion_rounds_correctly(converter):
    """AUD result should round to 2 decimal places."""
    conv, mock_rba = converter
    mock_rba.get_rate.return_value = Decimal("1.5523")
    aud, _ = conv.convert(Decimal("10.00"), "USD", datetime.date(2025, 10, 1))
    assert aud == Decimal("15.52")


def test_manual_override(converter):
    """manual_override should multiply amount by the supplied rate."""
    conv, _ = converter
    aud, rate = conv.manual_override(Decimal("50.00"), Decimal("1.60"))
    assert aud == Decimal("80.00")
    assert rate == Decimal("1.60")
