from flask import Blueprint, render_template
from flask_login import login_required
from ..services.tax_report_service import TaxReportService

reports_bp = Blueprint("reports", __name__)
_service = TaxReportService()


@reports_bp.route("/report")
@login_required
def report():
    summary = _service.generate_summary()
    return render_template("reports/summary.html", summary=summary)
