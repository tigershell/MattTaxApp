from typing import Optional
from ..extensions import db


class Vendor(db.Model):
    """Configuration record for one service provider.

    Stores how the app should treat each vendor — currency, GST status,
    ATO category, whether an API sync is available, etc. No API credentials
    are stored here; those live in the .env file.
    """

    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    api_available = db.Column(db.Boolean, nullable=False, default=False)
    default_currency = db.Column(db.String(3), nullable=False, default="USD")
    charges_gst = db.Column(db.Boolean, nullable=False, default=False)
    ato_category = db.Column(db.String(100), nullable=False, default="Software & Subscriptions")
    sync_frequency = db.Column(db.String(20), nullable=False, default="on_demand")  # monthly / on_demand
    pdf_required = db.Column(db.Boolean, nullable=False, default=True)
    billing_url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    expenses = db.relationship("Expense", backref="vendor", lazy=True)

    def __repr__(self) -> str:
        return f"<Vendor {self.name}>"
