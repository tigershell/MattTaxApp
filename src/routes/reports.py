from flask import Blueprint, render_template, request
from flask_login import login_required
from ..services.tax_report_service import TaxReportService

reports_bp = Blueprint("reports", __name__)
_service = TaxReportService()


@reports_bp.route("/report")
@login_required
def report():
    """Tax summary for a financial year.

    Defaults to the current financial year. Pass ?year=<financial_year_id> to
    view a past one — this is what the Financial Years page links to.
    """
    year_id = request.args.get("year", type=int)
    summary = _service.generate_summary(year_id=year_id)
    return render_template("reports/summary.html", summary=summary)
