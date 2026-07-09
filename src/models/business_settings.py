import datetime
from typing import Optional

from flask import g, has_app_context

from ..extensions import db

# Key used to memoise the settings row on Flask's per-request `g` object.
_CACHE_KEY = "_business_settings"


class BusinessSettings(db.Model):
    """App-wide business configuration — a single row.

    GST registration is a one-time fact about the business: once you register
    with the ATO you stay registered until you cancel. It is NOT something that
    restarts each financial year, so it lives here rather than on FinancialYear.

    Storing it per-year (as this app previously did) meant every new financial
    year appeared unregistered, silently disabling Input Tax Credits on that
    year's expenses.
    """

    __tablename__ = "business_settings"

    id = db.Column(db.Integer, primary_key=True)
    gst_registration_date = db.Column(db.Date, nullable=True)  # None = never registered

    @classmethod
    def get(cls) -> "BusinessSettings":
        """Return the settings row for reading.

        This method NEVER writes to the database. If no row exists yet it
        returns an unsaved default (registration date of None), because
        gst_applies() is called from inside request handlers that may have
        their own uncommitted changes pending — committing here would flush
        a half-built expense to disk.

        The result is memoised on Flask's `g` for the life of the request,
        since building a tax report calls this once per expense and income
        record.
        """
        if has_app_context() and _CACHE_KEY in g:
            return g.get(_CACHE_KEY)

        settings = cls.query.first()
        if settings is None:
            settings = cls()  # transient default — deliberately not added to the session

        if has_app_context():
            setattr(g, _CACHE_KEY, settings)
        return settings

    @classmethod
    def get_or_create(cls) -> "BusinessSettings":
        """Return the settings row, inserting it if missing.

        Use this when about to write a setting. Unlike get(), this commits.
        """
        settings = cls.query.first()
        if settings is None:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
            cls.clear_cache()
        return settings

    @staticmethod
    def clear_cache() -> None:
        """Drop the memoised row so the next get() re-reads from the database."""
        if has_app_context() and _CACHE_KEY in g:
            g.pop(_CACHE_KEY)

    def is_gst_registered_on(self, date: datetime.date) -> bool:
        """Return True if GST registration was active on the given date."""
        if not self.gst_registration_date:
            return False
        return date >= self.gst_registration_date

    @property
    def is_registered(self) -> bool:
        """True once a GST registration date has been recorded."""
        return self.gst_registration_date is not None

    def __repr__(self) -> str:
        return f"<BusinessSettings gst_registration_date={self.gst_registration_date}>"