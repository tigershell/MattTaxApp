import logging
from ..extensions import db

logger = logging.getLogger(__name__)

# Pre-configured vendor data based on Matt's actual service toolchain.
# api_available reflects v1 scope: Railway is the only API sync in v1.
VENDOR_SEED_DATA = [
    {
        "name": "Anthropic",
        "api_available": False,   # Usage API exists but PDF upload used in v1
        "default_currency": "AUD",
        "charges_gst": True,      # Anthropic invoices Matt in AUD + GST
        "ato_category": "Software & Subscriptions",
        "sync_frequency": "on_demand",
        "pdf_required": True,
        "notes": "AI API — invoiced in AUD with GST. PDF upload only in v1.",
    },
    {
        "name": "Railway",
        "api_available": True,    # GraphQL billing API — v1 integration
        "default_currency": "USD",
        "charges_gst": False,
        "ato_category": "Domain & Hosting",
        "sync_frequency": "monthly",
        "pdf_required": True,
        "notes": "Cloud hosting — API sync available. PDFs downloaded from Railway dashboard.",
    },
    {
        "name": "OpenAI",
        "api_available": False,   # Usage API exists but deferred to post-v1
        "default_currency": "USD",
        "charges_gst": False,
        "ato_category": "Software & Subscriptions",
        "sync_frequency": "on_demand",
        "pdf_required": True,
        "notes": "AI API — PDF upload only in v1.",
    },
    {
        "name": "Fal.ai",
        "api_available": False,   # Limited billing API — deferred to post-v1
        "default_currency": "USD",
        "charges_gst": False,
        "ato_category": "Software & Subscriptions",
        "sync_frequency": "on_demand",
        "pdf_required": True,
        "notes": "AI image API — PDF upload only in v1.",
    },
    {
        "name": "Netlify",
        "api_available": False,   # No billing API for non-enterprise
        "default_currency": "USD",
        "charges_gst": False,
        "ato_category": "Domain & Hosting",
        "sync_frequency": "on_demand",
        "pdf_required": True,
        "notes": "Static hosting — no billing API. PDF upload only.",
    },
    {
        "name": "Namecheap",
        "api_available": False,   # Account balance API only, no invoice retrieval
        "default_currency": "USD",
        "charges_gst": False,
        "ato_category": "Domain & Hosting",
        "sync_frequency": "on_demand",
        "pdf_required": True,
        "notes": "Domain registrar — no billing API. PDF upload only.",
    },
]


class DatabaseSeeder:
    """Seeds the database with required reference data.

    Safe to run multiple times — checks for existing records before inserting,
    so re-running will not create duplicates.
    """

    def seed_vendors(self) -> int:
        """Insert the pre-configured vendor list if they don't already exist.

        Returns:
            Number of new vendors created (0 if all already existed).
        """
        from ..models.vendor import Vendor

        created = 0
        for data in VENDOR_SEED_DATA:
            existing = Vendor.query.filter_by(name=data["name"]).first()
            if not existing:
                vendor = Vendor(**data)
                db.session.add(vendor)
                created += 1
                logger.info("Seeded vendor: %s", data["name"])

        if created:
            db.session.commit()

        return created

    def seed_current_financial_year(self) -> bool:
        """Create the current financial year record if it doesn't exist.

        Returns:
            True if a new FY was created, False if it already existed.
        """
        from ..models.financial_year import FinancialYear

        fy = FinancialYear.get_or_create_current()
        created = db.session.new and fy in db.session.new
        return bool(created)
