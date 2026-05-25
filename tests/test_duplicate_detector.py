import datetime
from decimal import Decimal

import pytest

from src.logic.duplicate_detector import DuplicateDetector
from src.models.expense import Expense, ExpenseSource
from src.models.financial_year import FinancialYear
from src.models.vendor import Vendor


@pytest.fixture
def seed_data(db, app):
    """Create a vendor, financial year, and one existing expense."""
    with app.app_context():
        vendor = Vendor(
            name="TestVendor",
            api_available=False,
            default_currency="USD",
            charges_gst=False,
            ato_category="Software & Subscriptions",
            sync_frequency="on_demand",
            pdf_required=True,
        )
        db.session.add(vendor)

        fy = FinancialYear(
            label="FY 2025-26",
            start_date=datetime.date(2025, 7, 1),
            end_date=datetime.date(2026, 6, 30),
        )
        db.session.add(fy)
        db.session.flush()

        expense = Expense(
            vendor_id=vendor.id,
            financial_year_id=fy.id,
            invoice_date=datetime.date(2025, 10, 15),
            amount_original=Decimal("100.00"),
            currency="USD",
            amount_aud=Decimal("155.00"),
            ato_category="Software & Subscriptions",
            source=ExpenseSource.api_sync,
            invoice_attached=False,
        )
        db.session.add(expense)
        db.session.commit()

        yield vendor, fy, expense


def test_exact_match(seed_data, app):
    """An exact vendor + date + amount match should be found."""
    vendor, _, expense = seed_data
    with app.app_context():
        detector = DuplicateDetector()
        match = detector.find_match(vendor.id, datetime.date(2025, 10, 15), Decimal("155.00"))
        assert match is not None
        assert match.id == expense.id


def test_match_within_date_tolerance(seed_data, app):
    """A date 1 day off should still match."""
    vendor, _, expense = seed_data
    with app.app_context():
        detector = DuplicateDetector()
        match = detector.find_match(vendor.id, datetime.date(2025, 10, 16), Decimal("155.00"))
        assert match is not None


def test_match_within_amount_tolerance(seed_data, app):
    """An amount off by $0.01 should still match."""
    vendor, _, expense = seed_data
    with app.app_context():
        detector = DuplicateDetector()
        match = detector.find_match(vendor.id, datetime.date(2025, 10, 15), Decimal("155.01"))
        assert match is not None


def test_no_match_different_vendor(seed_data, app):
    """A different vendor_id should not match."""
    with app.app_context():
        detector = DuplicateDetector()
        match = detector.find_match(9999, datetime.date(2025, 10, 15), Decimal("155.00"))
        assert match is None


def test_no_match_date_too_far(seed_data, app):
    """A date more than 1 day off should not match."""
    vendor, _, _ = seed_data
    with app.app_context():
        detector = DuplicateDetector()
        match = detector.find_match(vendor.id, datetime.date(2025, 10, 17), Decimal("155.00"))
        assert match is None


def test_no_match_amount_too_far(seed_data, app):
    """An amount more than $0.01 off should not match."""
    vendor, _, _ = seed_data
    with app.app_context():
        detector = DuplicateDetector()
        match = detector.find_match(vendor.id, datetime.date(2025, 10, 15), Decimal("156.00"))
        assert match is None
