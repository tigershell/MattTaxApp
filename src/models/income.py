import datetime
import enum
from decimal import Decimal
from ..extensions import db


class IncomeSource(enum.Enum):
    """How the income record was created."""
    manual = "manual"       # Entered manually by the user
    stripe = "stripe"       # Stripe payment (manual entry now, API sync later)
    api_sync = "api_sync"   # Created automatically from an API sync


class Income(db.Model):
    """A single business income (sale) record — the income-side mirror of Expense.

    Stores the gross AUD amount received and, when the sale is a taxable supply
    made on or after the GST registration date, the GST component collected
    (output tax owed to the ATO on the next BAS).

    GST treatment reuses the same registration-date logic as expenses
    (FinancialYear.is_gst_registered_on). Income received BEFORE the GST
    registration date carries no GST: the full amount is assessable income and
    nothing is payable to the ATO. This is exactly the case for a sale made on
    a setup that pre-dates GST registration.
    """

    __tablename__ = "income"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key — every income record is scoped to a financial year
    financial_year_id = db.Column(db.Integer, db.ForeignKey("financial_years.id"), nullable=False)

    # Core figures
    received_date = db.Column(db.Date, nullable=False)         # Date the income was received / invoiced
    amount_aud = db.Column(db.Numeric(10, 2), nullable=False)  # Gross amount received, in AUD
    gst_amount = db.Column(db.Numeric(10, 2), nullable=True)   # GST collected (output tax), if applicable

    # Reference / classification
    source_name = db.Column(db.String(150), nullable=True)     # Who paid / platform, e.g. "Stripe", customer name
    invoice_number = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Audit
    source = db.Column(db.Enum(IncomeSource), nullable=False, default=IncomeSource.manual)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    financial_year = db.relationship("FinancialYear", backref="income_records")

    def gst_applies(self) -> bool:
        """Return True if GST should be treated as collected on this income.

        True only when the financial year has a GST registration date set and
        this income was received on or after it. Pre-registration income is
        GST-free.
        """
        if not self.financial_year:
            return False
        return self.financial_year.is_gst_registered_on(self.received_date)

    def gst_payable(self) -> Decimal:
        """Return the GST collected on this income that is owed to the ATO.

        Zero unless GST applies (registered, on/after the registration date)
        AND a GST amount has been recorded. This is an output tax for the BAS,
        not an income tax figure.
        """
        if self.gst_applies() and self.gst_amount:
            return Decimal(str(self.gst_amount))
        return Decimal("0.00")

    def assessable_amount(self) -> Decimal:
        """Return the income-tax-assessable portion of this income, in AUD.

        Pre-GST registration: the full amount is assessable income.
        Post-GST registration: the GST collected is excluded (it is owed to the
        ATO, not income), so only the ex-GST amount is assessable.
        """
        return Decimal(str(self.amount_aud)) - self.gst_payable()

    def formatted_amount(self) -> str:
        return f"${self.amount_aud:,.2f}"

    def formatted_date(self) -> str:
        return self.received_date.strftime("%d %b %Y") if self.received_date else ""

    def __repr__(self) -> str:
        return f"<Income {self.id} {self.received_date} ${self.amount_aud}>"
