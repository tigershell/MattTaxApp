import datetime
from decimal import Decimal

from src.extensions import db as _db
from src.models.business_settings import BusinessSettings
from src.models.expense import Expense, ExpenseSource
from src.models.financial_year import FinancialYear
from src.models.income import Income
from src.models.vendor import Vendor
from src.services.tax_report_service import TaxReportService


def _set_gst_date(date):
    """Set the business-wide GST registration date."""
    settings = BusinessSettings.get_or_create()
    settings.gst_registration_date = date
    _db.session.commit()
    BusinessSettings.clear_cache()
    return settings


def _make_year(start_year: int) -> FinancialYear:
    """Create the Australian FY beginning 1 Jul of start_year."""
    fy = FinancialYear(
        label=f"FY {start_year}-{str(start_year + 1)[-2:]}",
        start_date=datetime.date(start_year, 7, 1),
        end_date=datetime.date(start_year + 1, 6, 30),
    )
    _db.session.add(fy)
    _db.session.commit()
    return fy


# --- The bug this change fixes ----------------------------------------------

def test_gst_registration_carries_into_later_financial_years(app):
    """Registering mid-FY2025-26 must still apply in FY2026-27.

    This is the regression test for the original bug: gst_registration_date
    lived on FinancialYear, so each new year started unregistered and its
    expenses silently lost their Input Tax Credits.
    """
    _set_gst_date(datetime.date(2026, 5, 12))

    fy_2526 = _make_year(2025)
    fy_2627 = _make_year(2026)

    vendor = Vendor(name="Anthropic", charges_gst=True, default_currency="AUD")
    _db.session.add(vendor)
    _db.session.commit()

    # An expense in the NEXT financial year, well after registration.
    later = Expense(
        vendor_id=vendor.id,
        financial_year_id=fy_2627.id,
        invoice_date=datetime.date(2026, 9, 1),
        amount_original=Decimal("110.00"),
        currency="AUD",
        amount_aud=Decimal("110.00"),
        gst_amount=Decimal("10.00"),
        ato_category="Software & Subscriptions",
        source=ExpenseSource.manual,
    )
    _db.session.add(later)
    _db.session.commit()

    assert later.gst_applies() is True
    assert later.deductible_amount() == Decimal("100.00")  # ex-GST; $10 is an ITC

    # And the year it was registered in still behaves correctly.
    assert fy_2526.gst_applies_during(datetime.date(2026, 5, 12)) is True
    assert fy_2627.gst_applies_during(datetime.date(2026, 5, 12)) is True


def test_expense_before_registration_is_fully_deductible(app):
    """An expense dated before registration keeps its GST in the deduction."""
    _set_gst_date(datetime.date(2026, 5, 12))
    fy = _make_year(2025)

    vendor = Vendor(name="Anthropic", charges_gst=True, default_currency="AUD")
    _db.session.add(vendor)
    _db.session.commit()

    early = Expense(
        vendor_id=vendor.id,
        financial_year_id=fy.id,
        invoice_date=datetime.date(2026, 1, 15),  # before registration
        amount_original=Decimal("110.00"),
        currency="AUD",
        amount_aud=Decimal("110.00"),
        gst_amount=Decimal("10.00"),
        ato_category="Software & Subscriptions",
        source=ExpenseSource.manual,
    )
    _db.session.add(early)
    _db.session.commit()

    assert early.gst_applies() is False
    assert early.deductible_amount() == Decimal("110.00")


def test_income_gst_carries_into_later_years(app):
    """Income GST also follows the business-wide registration date."""
    _set_gst_date(datetime.date(2026, 5, 12))
    fy_2627 = _make_year(2026)

    sale = Income(
        financial_year_id=fy_2627.id,
        received_date=datetime.date(2026, 8, 1),
        amount_aud=Decimal("1100.00"),
        gst_amount=Decimal("100.00"),
    )
    _db.session.add(sale)
    _db.session.commit()

    assert sale.gst_applies() is True
    assert sale.gst_payable() == Decimal("100.00")
    assert sale.assessable_amount() == Decimal("1000.00")


# --- Settings singleton behaviour -------------------------------------------

def test_get_does_not_write_to_the_database(app):
    """get() must never insert — it is called mid-request with pending changes."""
    assert BusinessSettings.query.count() == 0

    settings = BusinessSettings.get()

    assert settings.gst_registration_date is None
    assert settings.is_registered is False
    assert BusinessSettings.query.count() == 0  # still nothing persisted


def test_get_or_create_inserts_exactly_one_row(app):
    """get_or_create() is idempotent — the settings table stays a singleton."""
    first = BusinessSettings.get_or_create()
    BusinessSettings.clear_cache()
    second = BusinessSettings.get_or_create()

    assert first.id == second.id
    assert BusinessSettings.query.count() == 1


def test_clearing_the_date_disables_gst(app):
    """Clearing registration makes everything GST-free again."""
    _set_gst_date(datetime.date(2026, 5, 12))
    _set_gst_date(None)

    settings = BusinessSettings.get()
    assert settings.is_registered is False
    assert settings.is_gst_registered_on(datetime.date(2027, 1, 1)) is False


# --- Year-level interpretation of a single registration date -----------------

def test_gst_status_for_year_before_registration(app):
    """A year that ended before registration has no GST at all."""
    fy = _make_year(2024)  # ends 30 Jun 2025
    reg = datetime.date(2026, 5, 12)

    assert fy.gst_applies_during(reg) is False
    assert fy.gst_status(reg) == "Not GST registered"


def test_gst_status_for_year_of_registration(app):
    """The year registration happened is registered from that date onward."""
    fy = _make_year(2025)  # 1 Jul 2025 – 30 Jun 2026
    reg = datetime.date(2026, 5, 12)

    assert fy.gst_applies_during(reg) is True
    assert fy.gst_status(reg) == "GST registered from 12 May 2026"


def test_gst_status_for_year_after_registration(app):
    """A year starting after registration is registered for its whole duration."""
    fy = _make_year(2026)  # 1 Jul 2026 – 30 Jun 2027
    reg = datetime.date(2026, 5, 12)

    assert fy.gst_applies_during(reg) is True
    assert fy.gst_status(reg) == "GST registered (whole year)"


def test_gst_status_when_never_registered(app):
    """No registration date means no GST, in any year."""
    fy = _make_year(2026)

    assert fy.gst_applies_during(None) is False
    assert fy.gst_status(None) == "Not GST registered"


# --- Reporting on a specific (past) year ------------------------------------

def test_summary_scopes_to_the_requested_year(app):
    """generate_summary(year_id=...) reports only that year's records."""
    _set_gst_date(datetime.date(2026, 5, 12))
    fy_2526 = _make_year(2025)
    fy_2627 = _make_year(2026)

    _db.session.add(Income(
        financial_year_id=fy_2526.id,
        received_date=datetime.date(2026, 6, 1),
        amount_aud=Decimal("1100.00"),
        gst_amount=Decimal("100.00"),
    ))
    _db.session.add(Income(
        financial_year_id=fy_2627.id,
        received_date=datetime.date(2026, 8, 1),
        amount_aud=Decimal("2200.00"),
        gst_amount=Decimal("200.00"),
    ))
    _db.session.commit()

    older = TaxReportService().generate_summary(year_id=fy_2526.id)
    newer = TaxReportService().generate_summary(year_id=fy_2627.id)

    assert older["financial_year"] == "FY 2025-26"
    assert older["income_count"] == 1
    assert older["total_assessable_income"] == Decimal("1000.00")
    assert older["gst_status"] == "GST registered from 12 May 2026"

    assert newer["financial_year"] == "FY 2026-27"
    assert newer["income_count"] == 1
    assert newer["total_assessable_income"] == Decimal("2000.00")
    assert newer["gst_status"] == "GST registered (whole year)"
