import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from ..extensions import db
from ..models.business_settings import BusinessSettings
from ..models.expense import Expense
from ..models.financial_year import FinancialYear
from ..models.income import Income

years_bp = Blueprint("years", __name__)


@years_bp.route("/years")
@login_required
def list_years():
    """List all financial years, most recent first, with their record counts.

    Each year links through to its own tax summary. The GST registration date
    is shown once for the whole business rather than per year — it is a
    one-time registration, not something that restarts each July.
    """
    years = FinancialYear.query.order_by(FinancialYear.start_date.desc()).all()

    counts = {
        fy.id: {
            "expenses": Expense.query.filter_by(financial_year_id=fy.id).count(),
            "income": Income.query.filter_by(financial_year_id=fy.id).count(),
        }
        for fy in years
    }

    return render_template("years/list.html", years=years, counts=counts)


@years_bp.route("/settings/gst-registration-date", methods=["POST"])
@login_required
def set_gst_date():
    """Set or clear the business-wide GST registration date.

    Applies to every financial year at once: expenses and income dated on or
    after this date are treated as GST-bearing, everything before it is
    GST-free. Submitting an empty value clears the registration.
    """
    date_str = request.form.get("gst_registration_date", "").strip()
    settings = BusinessSettings.get_or_create()

    if not date_str:
        settings.gst_registration_date = None
        db.session.commit()
        BusinessSettings.clear_cache()
        flash("GST registration date cleared. No GST will be tracked.")
        return redirect(url_for("years.list_years"))

    try:
        parsed = datetime.date.fromisoformat(date_str)
    except ValueError:
        flash("Invalid date format. Use YYYY-MM-DD.", "error")
        return redirect(url_for("years.list_years"))

    settings.gst_registration_date = parsed
    db.session.commit()
    BusinessSettings.clear_cache()
    flash(f"GST registration date set to {parsed.strftime('%d %b %Y')} for all financial years.")
    return redirect(url_for("years.list_years"))
