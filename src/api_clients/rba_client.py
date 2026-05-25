import datetime
import logging
from decimal import Decimal
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.frankfurter.app"


class RBAClientError(Exception):
    """Raised when the exchange rate API is unreachable or returns an error."""


class RBAClient:
    """Fetches historical exchange rates via the Frankfurter API (api.frankfurter.app).

    Frankfurter is free, requires no API key, and provides daily rates back to
    1999 sourced from the European Central Bank. Rates are expressed as AUD per
    1 unit of foreign currency (e.g. rate=1.55 means 1 USD = 1.55 AUD).

    Caches every fetched rate in the RBARate table so duplicate lookups never
    hit the network.
    """

    def get_rate(self, rate_date: datetime.date, currency_code: str) -> Decimal:
        """Return the AUD exchange rate for the given date and currency.

        Checks the DB cache first. On a cache miss, fetches from Frankfurter
        and saves the result. Weekends/holidays fall back to the nearest
        prior business day automatically.

        Args:
            rate_date: The invoice date to look up.
            currency_code: ISO 4217 code, e.g. "USD".

        Returns:
            The rate as a Decimal (AUD per 1 unit of foreign currency).

        Raises:
            RBAClientError: If the API call fails and no cached rate exists.
        """
        cached = self._check_cache(rate_date, currency_code)
        if cached is not None:
            logger.info("Rate cache hit: %s %s = %s AUD", currency_code, rate_date, cached)
            return cached

        rate = self._fetch_from_api(rate_date, currency_code)
        self._save_to_cache(rate_date, currency_code, rate)
        return rate

    def _check_cache(self, rate_date: datetime.date, currency_code: str) -> Optional[Decimal]:
        """Return a cached rate, or None if not in the DB."""
        from ..models.rba_rate import RBARate
        record = RBARate.query.filter_by(
            rate_date=rate_date,
            currency_code=currency_code.upper(),
        ).first()
        return Decimal(str(record.rate)) if record else None

    def _fetch_from_api(self, rate_date: datetime.date, currency_code: str) -> Decimal:
        """Call Frankfurter and return AUD per 1 unit of foreign currency."""
        date_str = rate_date.strftime("%Y-%m-%d")
        url = f"{BASE_URL}/{date_str}"
        params = {"from": currency_code.upper(), "to": "AUD"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise RBAClientError("Exchange rate API request timed out.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise RBAClientError(
                    f"No exchange rate available for {date_str} {currency_code} — "
                    "date may be too recent or a non-trading day."
                )
            else:
                raise RBAClientError(f"Exchange rate API error: {e}")
        except requests.exceptions.RequestException as e:
            raise RBAClientError(f"Exchange rate API unreachable: {e}")

        data = response.json()
        logger.info("Frankfurter fetched: %s %s -> %s", currency_code, date_str, data)

        try:
            rate_value = data["rates"]["AUD"]
        except (KeyError, TypeError):
            raise RBAClientError(
                f"Could not parse AUD rate from API response: {data}"
            )

        # Frankfurter returns AUD per 1 unit of foreign currency directly — no inversion needed.
        return Decimal(str(rate_value))

    def _save_to_cache(
        self, rate_date: datetime.date, currency_code: str, rate: Decimal
    ) -> None:
        """Persist a fetched rate to the RBARate cache table."""
        from ..models.rba_rate import RBARate
        from ..extensions import db

        record = RBARate(
            rate_date=rate_date,
            currency_code=currency_code.upper(),
            rate=rate,
        )
        db.session.add(record)
        db.session.commit()
        logger.info("Rate cached: %s %s = %s AUD", currency_code, rate_date, rate)