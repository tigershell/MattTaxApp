import datetime
import enum
from decimal import Decimal
from typing import Optional
from ..extensions import db


class ExpenseSource(enum.Enum):
    """How the expense record was created."""
    api_sync = "api_sync"       # Created automatically from an API sync
    pdf_upload = "pdf_upload"   # Created from a PDF upload
    manual = "manual"           # Entered manually by the user


ATO_CATEGORIES = [
    "Software & Subscriptions",
    "Domain & Hosting",
    "Legal & Professional",
    "Other Business Expenses",
]


class Expense(db.Model):
    """A single deductible business expense record.

    Stores both the original currency amount and the AUD equivalent. When
    gst_amount is set and GST rules apply, the deductible amount is the
    ex-GST portion only. Otherwise the full amount_aud is deductible.
    """

    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False)
    financial_year_id = db.Column(db.Integer, db.ForeignKey("financial_years.id"), nullable=False)

    # Invoice details
    invoice_date = db.Column(db.Date, nullable=False)
    amount_original = db.Column(db.Numeric(10, 2), nullable=False)  # In original currency
    currency = db.Column(db.String(3), nullable=False, default="AUD")
    rba_rate = db.Column(db.Numeric(10, 6), nullable=True)           # Null for AUD expenses
    amount_aud = db.Column(db.Numeric(10, 2), nullable=False)        # Always in AUD
    gst_amount = db.Column(db.Numeric(10, 2), nullable=True)         # GST component if applicable

    # Invoice reference
    invoice_number = db.Column(db.String(100), nullable=True)

    # Classification
    ato_category = db.Column(db.String(100), nullable=False, default="Software & Subscriptions")
    description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # PDF attachment
    pdf_data = db.Column(db.LargeBinary, nullable=True)
    invoice_attached = db.Column(db.Boolean, nullable=False, default=False)

    # Audit
    source = db.Column(db.Enum(ExpenseSource), nullable=False, default=ExpenseSource.manual)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def gst_applies(self) -> bool:
        """Return True if GST rules should split this expense's amount.

        Requires the vendor to charge GST AND the financial year to have
        a GST registration date set AND the invoice date to be on or after
        that registration date.
        """
        if not self.vendor or not self.financial_year:
            return False
        if not self.vendor.charges_gst:
            return False
        return self.financial_year.is_gst_registered_on(self.invoice_date)

    def deductible_amount(self) -> Decimal:
        """Return the ATO-deductible portion of this expense in AUD.

        Pre-GST registration: the full AUD amount is deductible.
        Post-GST registration: the ex-GST amount is deductible (GST becomes an ITC).
        """
        if self.gst_applies() and self.gst_amount:
            return Decimal(str(self.amount_aud)) - Decimal(str(self.gst_amount))
        return Decimal(str(self.amount_aud))

    def formatted_amount(self) -> str:
        return f"${self.amount_aud:,.2f}"

    def formatted_date(self) -> str:
        return self.invoice_date.strftime("%d %b %Y") if self.invoice_date else ""

    def __repr__(self) -> str:
        return f"<Expense {self.id} {self.vendor_id} {self.invoice_date} ${self.amount_aud}>"
