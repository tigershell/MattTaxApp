from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from ..services.expense_service import ExpenseService
from ..models.expense import ATO_CATEGORIES

expenses_bp = Blueprint("expenses", __name__)
_service = ExpenseService()


@expenses_bp.route("/expenses")
@login_required
def list_expenses():
    expenses = _service.get_all()
    return render_template("expenses/list.html", expenses=expenses)


@expenses_bp.route("/expenses/<int:expense_id>")
@login_required
def detail(expense_id: int):
    expense = _service.get_by_id(expense_id)
    return render_template("expenses/detail.html", expense=expense)


@expenses_bp.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit(expense_id: int):
    expense = _service.get_by_id(expense_id)
    if request.method == "POST":
        _service.update(expense_id, request.form)
        flash("Expense updated.")
        return redirect(url_for("expenses.detail", expense_id=expense_id))
    return render_template("expenses/edit.html", expense=expense, categories=ATO_CATEGORIES)


@expenses_bp.route("/expenses/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete(expense_id: int):
    _service.delete(expense_id)
    flash("Expense deleted.")
    return redirect(url_for("expenses.list_expenses"))
