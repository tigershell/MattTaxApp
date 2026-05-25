import io
import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, abort, send_file, request, redirect, url_for, flash
from flask_login import login_required

from ..extensions import db
from ..models.expense import Expense, ATO_CATEGORIES
from ..models.financial_year import FinancialYear
from ..models.vendor import Vendor

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/expenses")
@login_required
def list_expenses():
    """List all expenses for the current financial year."""
    fy = FinancialYear.get_or_create_current()
    expenses = (
        Expense.query
        .filter_by(financial_year_id=fy.id)
        .order_by(Expense.invoice_date.desc())
        .all()
    )
    return render_template("expenses/list.html", expenses=expenses, fy=fy)


@expenses_bp.route("/expenses/<int:expense_id>")
@login_required
def detail(expense_id: int):
    """Show a single expense record."""
    expense = Expense.query.get_or_404(expense_id)
    return render_template("expenses/detail.html", expense=expense)


@expenses_bp.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit(expense_id: int):
    """Edit an existing expense record."""
    expense = Expense.query.get_or_404(expense_id)
    vendors = Vendor.query.order_by(Vendor.name).all()

    if request.method == "POST":
        try:
            expense.vendor_id = int(request.form["vendor_id"])
            expense.invoice_date = datetime.date.fromisoformat(request.form["invoice_date"])
            expense.currency = request.form["currency"].upper().strip()
            expense.amount_original = Decimal(request.form["amount_original"])
            expense.amount_aud = Decimal(request.form["amount_aud"])
            expense.ato_category = request.form["ato_category"]
            expense.description = request.form.get("description", "").strip() or None
            expense.notes = request.form.get("notes", "").strip() or None
            gst_str = request.form.get("gst_amount", "").strip()
            expense.gst_amount = Decimal(gst_str) if gst_str else None
            rba_str = request.form.get("rba_rate", "").strip()
            expense.rba_rate = Decimal(rba_str) if rba_str else None
        except (ValueError, InvalidOperation) as e:
            flash(f"Invalid value: {e}", "error")
            return render_template(
                "expenses/edit.html",
                expense=expense,
                vendors=vendors,
                ato_categories=ATO_CATEGORIES,
            )

        db.session.commit()
        flash("Expense updated.")
        return redirect(url_for("expenses.detail", expense_id=expense.id))

    return render_template(
        "expenses/edit.html",
        expense=expense,
        vendors=vendors,
        ato_categories=ATO_CATEGORIES,
    )


@expenses_bp.route("/expenses/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete(expense_id: int):
    """Delete an expense record."""
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash(f"Expense #{expense_id} deleted.")
    return redirect(url_for("expenses.list_expenses"))


@expenses_bp.route("/expenses/<int:expense_id>/pdf")
@login_required
def serve_pdf(expense_id: int):
    """Stream the stored PDF for an expense."""
    expense = Expense.query.get_or_404(expense_id)
    if not expense.pdf_data:
        abort(404)
    return send_file(
        io.BytesIO(expense.pdf_data),
        mimetype="application/pdf",
        download_name=f"invoice-{expense_id}.pdf",
    )
