import datetime
from typing import Optional
from ..extensions import db


class FinancialYear(db.Model):
    """An Australian financial year (1 Jul – 30 Jun).

    All expense and income records are scoped to a FinancialYear. Note that the
    GST registration date does NOT live here — it is a one-time property of the
    business and is stored on BusinessSettings. See gst_status() for how a
    single registration date is interpreted against a given year.
    """

    __tablename__ = "financial_years"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), unique=True, nullable=False)  # e.g. "FY 2025-26"
    start_date = db.Column(db.Date, nullable=False)                # 1 Jul YYYY
    end_date = db.Column(db.Date, nullable=False)                  # 30 Jun YYYY+1

    expenses = db.relationship("Expense", backref="financial_year", lazy=True)

    def contains(self, date: datetime.date) -> bool:
        """Return True if the given date falls inside this financial year."""
        return self.start_date <= date <= self.end_date

    def is_current(self) -> bool:
        """Return True if today falls inside this financial year."""
        return self.contains(datetime.date.today())

    def gst_applies_during(self, registration_date: Optional[datetime.date]) -> bool:
        """Return True if the business was GST registered at any point in this year.

        False for years that ended before the business ever registered — those
        years have no BAS position at all.
        """
        if registration_date is None:
            return False
        return registration_date <= self.end_date

    def gst_status(self, registration_date: Optional[datetime.date]) -> str:
        """Describe this year's GST position given the business registration date.

        A single registration date lands a year in one of three states:
          * registered before the year began  → registered for the whole year
          * registered part-way through it    → registered from that date on
          * registered after it ended, or not at all → not registered
        """
        if registration_date is None or registration_date > self.end_date:
            return "Not GST registered"
        if registration_date <= self.start_date:
            return "GST registered (whole year)"
        return f"GST registered from {registration_date.strftime('%d %b %Y')}"

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
    def get_or_create_for_date(cls, date: datetime.date) -> "FinancialYear":
        """Return the FinancialYear containing `date`, creating it in the DB if needed.

        Records must be filed by their own date (invoice date, income received
        date) — never by today's date, or anything entered after 30 Jun lands
        in the wrong tax year.
        """
        if date.month >= 7:
            fy_start_year = date.year
        else:
            fy_start_year = date.year - 1

        label = f"FY {fy_start_year}-{str(fy_start_year + 1)[-2:]}"
        fy = cls.query.filter_by(label=label).first()
        if not fy:
            fy = cls.for_date(date)
            db.session.add(fy)
            db.session.commit()
        return fy

    @classmethod
    def get_or_create_current(cls) -> "FinancialYear":
        """Return the FinancialYear for today, creating it in the DB if needed."""
        return cls.get_or_create_for_date(datetime.date.today())

    def __repr__(self) -> str:
        return f"<FinancialYear {self.label}>"
