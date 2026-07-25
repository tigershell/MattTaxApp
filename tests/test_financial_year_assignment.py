import datetime

from src.models.financial_year import FinancialYear


def test_for_date_maps_dates_to_australian_fy():
    """Dates resolve to the FY containing them: 1 Jul – 30 Jun."""
    fy = FinancialYear.for_date(datetime.date(2026, 4, 23))
    assert fy.label == "FY 2025-26"
    assert fy.start_date == datetime.date(2025, 7, 1)
    assert fy.end_date == datetime.date(2026, 6, 30)

    assert FinancialYear.for_date(datetime.date(2026, 6, 30)).label == "FY 2025-26"
    assert FinancialYear.for_date(datetime.date(2026, 7, 1)).label == "FY 2026-27"


def test_get_or_create_for_date_files_by_record_date(app):
    """A record dated last FY must land in last FY, whatever today's date is.

    This guards against the bug where uploads were stamped with the *current*
    FY (today's date) instead of the invoice date, so invoices from FY 2025-26
    uploaded after 1 Jul 2026 appeared in FY 2026-27.
    """
    fy = FinancialYear.get_or_create_for_date(datetime.date(2026, 5, 23))
    assert fy.label == "FY 2025-26"
    assert fy.contains(datetime.date(2026, 5, 23))

    next_fy = FinancialYear.get_or_create_for_date(datetime.date(2026, 8, 1))
    assert next_fy.label == "FY 2026-27"
    assert next_fy.id != fy.id


def test_get_or_create_for_date_reuses_existing_row(app):
    """Two dates in the same FY share one row — no duplicate years created."""
    a = FinancialYear.get_or_create_for_date(datetime.date(2025, 9, 1))
    b = FinancialYear.get_or_create_for_date(datetime.date(2026, 2, 1))
    assert a.id == b.id
    assert FinancialYear.query.count() == 1


def test_get_or_create_current_matches_today(app):
    """The current-FY helper is just the date-based lookup applied to today."""
    fy = FinancialYear.get_or_create_current()
    assert fy.contains(datetime.date.today())
