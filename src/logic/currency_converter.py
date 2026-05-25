import datetime
import logging
from decimal import Decimal, ROUND_HALF_UP

from ..api_clients.rba_client import RBAClient, RBAClientError

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Converts foreign currency amounts to AUD using RBA exchange rates.

    AUD amounts pass through unchanged. For all other currencies, the rate
    is fetched (or retrieved from cache) via RBAClient.
    """

    def __init__(self) -> None:
        self._rba = RBAClient()

    def convert(
        self, amount: Decimal, currency: str, invoice_date: datetime.date
    ) -> tuple[Decimal, Decimal]:
        """Convert an amount to AUD using the RBA rate for the invoice date.

        Args:
            amount: The original currency amount.
            currency: ISO 4217 currency code (e.g. "USD", "AUD").
            invoice_date: The date the invoice was issued.

        Returns:
            A tuple of (aud_amount, rate_used). For AUD invoices the rate
            is always Decimal('1').

        Raises:
            RBAClientError: If the exchange rate cannot be fetched.
        """
        if currency.upper() == "AUD":
            return amount, Decimal("1")

        rate = self._rba.get_rate(invoice_date, currency.upper())
        aud_amount = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        logger.info(
            "Converted %s %s -> %s AUD (rate %s, date %s)",
            amount, currency, aud_amount, rate, invoice_date,
        )
        return aud_amount, rate

    def manual_override(self, amount: Decimal, rate: Decimal) -> tuple[Decimal, Decimal]:
        """Convert using a manually supplied rate (fallback when API is unavailable).

        Args:
            amount: The original currency amount.
            rate: AUD per 1 unit of foreign currency.

        Returns:
            A tuple of (aud_amount, rate_used).
        """
        aud_amount = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return aud_amount, rate
