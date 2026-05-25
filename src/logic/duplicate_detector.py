import datetime
import logging
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)

DATE_TOLERANCE_DAYS = 1
AMOUNT_TOLERANCE_AUD = Decimal("0.01")


class DuplicateDetector:
    """Checks whether an incoming expense record already exists in the DB.

    Used both when syncing from an API and when uploading a PDF — prevents
    creating duplicate records for the same invoice.

    Matching uses a small tolerance on date (±1 day) and amount (±$0.01 AUD)
    to handle minor rounding differences between data sources.
    """

    def find_match(
        self,
        vendor_id: int,
        invoice_date: datetime.date,
        amount_aud: Decimal,
    ) -> Optional[object]:
        """Search for an existing expense that matches the given parameters.

        Args:
            vendor_id: The vendor's DB id.
            invoice_date: The invoice date to match against.
            amount_aud: The AUD amount to match against.

        Returns:
            The matching Expense object, or None if no match is found.
        """
        from ..models.expense import Expense

        date_min = invoice_date - datetime.timedelta(days=DATE_TOLERANCE_DAYS)
        date_max = invoice_date + datetime.timedelta(days=DATE_TOLERANCE_DAYS)

        candidates = Expense.query.filter(
            Expense.vendor_id == vendor_id,
            Expense.invoice_date >= date_min,
            Expense.invoice_date <= date_max,
        ).all()

        for expense in candidates:
            if abs(Decimal(str(expense.amount_aud)) - amount_aud) <= AMOUNT_TOLERANCE_AUD:
                logger.info(
                    "Duplicate found: expense %s matches vendor=%s date=%s amount=%s",
                    expense.id, vendor_id, invoice_date, amount_aud,
                )
                return expense

        return None