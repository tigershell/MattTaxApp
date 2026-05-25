import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from ..extensions import db
from ..models.financial_year import FinancialYear

years_bp = Blueprint("years", __name__)


@years_bp.route("/years")
@login_required
def list_years():
    """List all financial years, most recent first."""
    years = FinancialYear.query.order_by(FinancialYear.start_date.desc()).all()
    return render_template("years/list.html", years=years)


@years_bp.route("/years/<int:year_id>/set-gst-date", methods=["POST"])
@login_required
def set_gst_date(year_id: int):
    """Set or clear the GST registration date for a financial year."""
    fy = FinancialYear.query.get_or_404(year_id)
    date_str = request.form.get("gst_registration_date", "").strip()

    if date_str:
        try:
            fy.gst_registration_date = datetime.date.fromisoformat(date_str)
            db.session.commit()
            flash(f"GST registration date set to {date_str} for {fy.label}.")
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
    else:
        fy.gst_registration_date = None
        db.session.commit()
        flash(f"GST registration date cleared for {fy.label}.")

    return redirect(url_for("years.list_years"))
