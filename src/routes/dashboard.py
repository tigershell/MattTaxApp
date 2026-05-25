from flask import Blueprint, render_template
from flask_login import login_required
from ..models.financial_year import FinancialYear
from ..models.expense import Expense

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Home page — current FY summary."""
    fy = FinancialYear.get_or_create_current()
    expenses = Expense.query.filter_by(financial_year_id=fy.id).all()

    total_aud = sum(e.amount_aud for e in expenses)
    unattached = sum(1 for e in expenses if not e.invoice_attached)

    return render_template(
        "dashboard/index.html",
        fy=fy,
        expense_count=len(expenses),
        total_aud=total_aud,
        unattached_count=unattached,
    )
