from decimal import Decimal
from collections import defaultdict

from flask import Blueprint, render_template
from flask_login import login_required
from ..models.financial_year import FinancialYear
from ..models.expense import Expense

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Home page — current FY summary with spend breakdowns."""
    fy = FinancialYear.get_or_create_current()
    expenses = Expense.query.filter_by(financial_year_id=fy.id).all()

    total_aud = sum(Decimal(str(e.amount_aud)) for e in expenses)
    unattached = sum(1 for e in expenses if not e.invoice_attached)

    # Spend by ATO category
    by_category = defaultdict(Decimal)
    for e in expenses:
        by_category[e.ato_category] += Decimal(str(e.amount_aud))
    by_category = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

    # Spend by vendor
    by_vendor = defaultdict(lambda: {"name": "", "total": Decimal("0"), "id": None})
    for e in expenses:
        by_vendor[e.vendor_id]["name"] = e.vendor.name
        by_vendor[e.vendor_id]["id"] = e.vendor_id
        by_vendor[e.vendor_id]["total"] += Decimal(str(e.amount_aud))
    by_vendor = sorted(by_vendor.values(), key=lambda x: x["total"], reverse=True)

    # Recent 5 expenses
    recent = sorted(expenses, key=lambda e: e.invoice_date, reverse=True)[:5]

    return render_template(
        "dashboard/index.html",
        fy=fy,
        expense_count=len(expenses),
        total_aud=total_aud,
        unattached_count=unattached,
        by_category=by_category,
        by_vendor=by_vendor,
        recent=recent,
    )