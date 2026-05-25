import datetime
from typing import Optional
from ..extensions import db


class FinancialYear(db.Model):
    """An Australian financial year (1 Jul – 30 Jun) and its GST config.

    All expense records are scoped to a FinancialYear. The gst_registration_date
    field is the dividing line between pre-GST (full deduction) and post-GST
    (GST split as Input Tax Credit) treatment for that year's expenses.
    """

    __tablename__ = "financial_years"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), unique=True, nullable=False)  # e.g. "FY 2025-26"
    start_date = db.Column(db.Date, nullable=False)                # 1 Jul YYYY
    end_date = db.Column(db.Date, nullable=False)                  # 30 Jun YYYY+1
    gst_registration_date = db.Column(db.Date, nullable=True)      # None = not yet registered

    expenses = db.relationship("Expense", backref="financial_year", lazy=True)

    def is_gst_registered_on(self, date: datetime.date) -> bool:
        """Return True if GST was active on the given date."""
        if not self.gst_registration_date:
            return False
        return date >= self.gst_registration_date

    @classmethod
    def for_date(cls, date: datetime.date) -> "FinancialYear":
        """Return the financial year that contains the given date.

        Australian FYs run 1 Jul to 30 Jun. If the month is July or later,
        the FY started this calendar year; otherwise it started last year.
        """
        if date.month >= 7:
            fy_start_year = date.year
        else:
            fy_start_year = date.year - 1

        start = datetime.date(fy_start_year, 7, 1)
        end = datetime.date(fy_start_year + 1, 6, 30)
        label = f"FY {fy_start_year}-{str(fy_start_year + 1)[-2:]}"
        return cls(label=label, start_date=start, end_date=end)

    @classmethod
    def get_or_create_current(cls) -> "FinancialYear":
        """Return the FinancialYear for today, creating it in the DB if needed."""
        today = datetime.date.today()
        if today.month >= 7:
            fy_start_year = today.year
        else:
            fy_start_year = today.year - 1

        label = f"FY {fy_start_year}-{str(fy_start_year + 1)[-2:]}"
        fy = cls.query.filter_by(label=label).first()
        if not fy:
            fy = cls.for_date(today)
            db.session.add(fy)
            db.session.commit()
        return fy

    def __repr__(self) -> str:
        return f"<FinancialYear {self.label}>"
