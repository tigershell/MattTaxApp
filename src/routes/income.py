import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..extensions import db
from ..models.income import Income, IncomeSource
from ..models.financial_year import FinancialYear

income_bp = Blueprint("income", __name__)


def _parse_form(form: dict) -> dict:
    """Parse and validate the income form into model fields.

    Raises:
        ValueError / InvalidOperation: if a date or number is malformed.
    """
    gst_str = form.get("gst_amount", "").strip()
    source_raw = form.get("source", "manual")
    try:
        source = IncomeSource(source_raw)
    except ValueError:
        source = IncomeSource.manual

    return {
        "received_date": datetime.date.fromisoformat(form["received_date"]),
        "amount_aud": Decimal(form["amount_aud"]),
        "gst_amount": Decimal(gst_str) if gst_str else None,
        "source": source,
        "source_name": form.get("source_name", "").strip() or None,
        "invoice_number": form.get("invoice_number", "").strip() or None,
        "description": form.get("description", "").strip() or None,
        "notes": form.get("notes", "").strip() or None,
    }


@income_bp.route("/income")
@login_required
def list_income():
    """List all income records for the current financial year."""
    fy = FinancialYear.get_or_create_current()
    records = (
        Income.query
        .filter_by(financial_year_id=fy.id)
        .order_by(Income.received_date.desc())
        .all()
    )
    total = sum(Decimal(str(r.amount_aud)) for r in records)
    return render_template("income/list.html", records=records, fy=fy, total=total)


@income_bp.route("/income/<int:income_id>")
@login_required
def detail(income_id: int):
    """Show a single income record."""
    record = Income.query.get_or_404(income_id)
    return render_template("income/detail.html", record=record)


@income_bp.route("/income/new", methods=["GET", "POST"])
@login_required
def new():
    """Record a business income / sale manually."""
    fy = FinancialYear.get_or_create_current()
    today = datetime.date.today().isoformat()

    if request.method == "POST":
        try:
            data = _parse_form(request.form)
        except (ValueError, InvalidOperation) as e:
            flash(f"Invalid form data: {e}", "error")
            return render_template("income/new.html", today=today, fy=fy, sources=IncomeSource)

        record = Income(financial_year_id=fy.id, **data)
        db.session.add(record)
        db.session.commit()

        flash(f"Income saved — ${record.amount_aud:,.2f} AUD ({record.formatted_date()}).")
        return redirect(url_for("income.detail", income_id=record.id))

    return render_template("income/new.html", today=today, fy=fy, sources=IncomeSource)


@income_bp.route("/income/<int:income_id>/edit", methods=["GET", "POST"])
@login_required
def edit(income_id: int):
    """Edit an existing income record."""
    record = Income.query.get_or_404(income_id)

    if request.method == "POST":
        try:
            data = _parse_form(request.form)
        except (ValueError, InvalidOperation) as e:
            flash(f"Invalid value: {e}", "error")
            return render_template("income/edit.html", record=record, sources=IncomeSource)

        for field, value in data.items():
            setattr(record, field, value)
        db.session.commit()

        flash("Income updated.")
        return redirect(url_for("income.detail", income_id=record.id))

    return render_template("income/edit.html", record=record, sources=IncomeSource)


@income_bp.route("/income/<int:income_id>/delete", methods=["POST"])
@login_required
def delete(income_id: int):
    """Delete an income record."""
    record = Income.query.get_or_404(income_id)
    db.session.delete(record)
    db.session.commit()
    flash(f"Income #{income_id} deleted.")
    return redirect(url_for("income.list_income"))
