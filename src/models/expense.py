from ..extensions import db
import datetime


ATO_CATEGORIES = [
    "Software & Subscriptions",
    "Domain & Hosting",
    "Legal & Professional",
    "Other Business Expenses",
]


class Expense(db.Model):
    """A single deductible business expense linked to a PDF invoice."""

    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(255), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    amount_aud = db.Column(db.Numeric(10, 2), nullable=False)
    ato_category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    document = db.relationship("Document", backref="expense", uselist=False)

    def formatted_amount(self) -> str:
        return f"${self.amount_aud:,.2f}"

    def formatted_date(self) -> str:
        return self.invoice_date.strftime("%-d %b %Y") if self.invoice_date else ""
