import datetime
from decimal import Decimal

from src.extensions import db as _db
from src.models.business_settings import BusinessSettings
from src.models.financial_year import FinancialYear
from src.models.vendor import Vendor
from src.models.expense import Expense, ExpenseSource
from src.models.income import Income, IncomeSource
from src.services.tax_report_service import TaxReportService


def _current_fy(reg_date=None):
    """Return the current financial year, setting the business-wide GST date.

    Uses get_or_create_current() so it matches the FY the report service loads,
    regardless of the machine's actual date. The GST registration date is a
    business-wide setting, not a property of the year.
    """
    settings = BusinessSettings.get_or_create()
    settings.gst_registration_date = reg_date
    _db.session.commit()
    BusinessSettings.clear_cache()
    return FinancialYear.get_or_create_current()


# --- Income model GST logic -------------------------------------------------

def test_income_pre_registration_has_no_gst(app):
    """Income dated before the GST registration date is GST-free and fully assessable."""
    fy = _current_fy(reg_date=datetime.date(2025, 1, 1))
    income = Income(
        financial_year_id=fy.id,
        received_date=datetime.date(2024, 6, 1),   # before registration
        amount_aud=Decimal("1100.00"),
        gst_amount=Decimal("100.00"),              # present, but must not apply
    )
    _db.session.add(income)
    _db.session.commit()

    assert income.gst_applies() is False
    assert income.gst_payable() == Decimal("0.00")
    assert income.assessable_amount() == Decimal("1100.00")


def test_income_post_registration_splits_gst(app):
    """Income on/after the registration date treats GST as collected output tax."""
    fy = _current_fy(reg_date=datetime.date(2025, 1, 1))
    income = Income(
        financial_year_id=fy.id,
        received_date=datetime.date(2025, 6, 1),   # after registration
        amount_aud=Decimal("1100.00"),
        gst_amount=Decimal("100.00"),
    )
    _db.session.add(income)
    _db.session.commit()

    assert income.gst_applies() is True
    assert income.gst_payable() == Decimal("100.00")
    assert income.assessable_amount() == Decimal("1000.00")


def test_income_not_registered_at_all(app):
    """With no registration date set, no income GST applies."""
    fy = _current_fy(reg_date=None)
    income = Income(
        financial_year_id=fy.id,
        received_date=datetime.date(2025, 6, 1),
        amount_aud=Decimal("500.00"),
    )
    _db.session.add(income)
    _db.session.commit()

    assert income.gst_applies() is False
    assert income.assessable_amount() == Decimal("500.00")


# --- Report integration -----------------------------------------------------

def test_report_combines_income_and_expenses(app):
    """The summary nets assessable income against deductible expenses and
    reports the GST/BAS position correctly."""
    fy = _current_fy(reg_date=datetime.date(2025, 1, 1))

    vendor = Vendor(name="Acme", charges_gst=True, default_currency="AUD")
    _db.session.add(vendor)
    _db.session.commit()

    # Post-registration sale: $1,100 incl $100 GST
    _db.session.add(Income(
        financial_year_id=fy.id,
        received_date=datetime.date(2025, 6, 1),
        amount_aud=Decimal("1100.00"),
        gst_amount=Decimal("100.00"),
        source=IncomeSource.stripe,
    ))
    # Post-registration purchase: $220 incl $20 GST
    _db.session.add(Expense(
        vendor_id=vendor.id,
        financial_year_id=fy.id,
        invoice_date=datetime.date(2025, 6, 2),
        amount_original=Decimal("220.00"),
        currency="AUD",
        amount_aud=Decimal("220.00"),
        gst_amount=Decimal("20.00"),
        ato_category="Software & Subscriptions",
        source=ExpenseSource.manual,
    ))
    _db.session.commit()

    summary = TaxReportService().generate_summary()

    # Income tax: assessable 1000, deductions 200 (ex-GST), net profit 800
    assert summary["total_assessable_income"] == Decimal("1000.00")
    assert summary["total_deductions"] == Decimal("200.00")
    assert summary["net_position"] == Decimal("800.00")
    assert summary["is_profit"] is True

    # GST / BAS: collected 100, paid 20, net 80 owed to the ATO
    assert summary["gst_collected"] == Decimal("100.00")
    assert summary["gst_paid"] == Decimal("20.00")
    assert summary["gst_net"] == Decimal("80.00")
