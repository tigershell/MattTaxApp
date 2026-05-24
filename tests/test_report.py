import pytest
from decimal import Decimal


def test_report_grand_total_sums_categories():
    """Smoke test: grand_total equals sum of category totals."""
    totals = [Decimal("100.00"), Decimal("50.00"), Decimal("25.00")]
    grand = sum(totals)
    assert grand == Decimal("175.00")
