import datetime
from decimal import Decimal
from ..extensions import db


class RBARate(db.Model):
    """Cached RBA exchange rate for one date and currency pair.

    Every rate fetched from exchangeratesapi.com.au is saved here so we
    never hit the API twice for the same date. The free tier allows only
    300 calls/month, so this cache is important to protect.
    """

    __tablename__ = "rba_rates"

    id = db.Column(db.Integer, primary_key=True)
    rate_date = db.Column(db.Date, nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)  # e.g. "USD"
    rate = db.Column(db.Numeric(10, 6), nullable=False)       # AUD per 1 unit of currency
    fetched_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("rate_date", "currency_code", name="uq_rba_rate_date_currency"),
    )

    def __repr__(self) -> str:
        return f"<RBARate {self.currency_code} {self.rate_date} = {self.rate}>"
