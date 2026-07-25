import io
import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, abort, send_file, request, redirect, url_for, flash
from flask_login import login_required

from ..extensions import db
from ..models.expense import Expense, ExpenseSource, ATO_CATEGORIES
from ..models.financial_year import FinancialYear
from ..models.vendor import Vendor
from ..logic.currency_converter import CurrencyConverter
from ..api_clients.rba_client import RBAClientError

expenses_bp = Blueprint("expenses", __name__)


def _detect_mimetype(data: bytes) -> tuple[str, str]:
    """Return (mime_type, file_extension) by inspecting magic bytes."""
    if data[:4] == b"%PDF":
        return "application/pdf", ".pdf"
    if data[:2] == b"\xff\xd8":
        return "image/jpeg", ".jpg"
    if data[:4] == b"\x89PNG":
        return "image/png", ".png"
    return "application/octet-stream", ".bin"


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
            expense.invoice_number = request.form.get("invoice_number", "").strip() or None
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

        # If the invoice date moved, re-file the expense under the right FY
        expense.financial_year_id = FinancialYear.get_or_create_for_date(expense.invoice_date).id
        db.session.commit()
        flash("Expense updated.")
        return redirect(url_for("expenses.detail", expense_id=expense.id))

    return render_template(
        "expenses/edit.html",
        expense=expense,
        vendors=vendors,
        ato_categories=ATO_CATEGORIES,
    )


@expenses_bp.route("/expenses/new", methods=["GET", "POST"])
@login_required
def new():
    """Create an expense record manually without uploading a document."""
    vendors = Vendor.query.order_by(Vendor.name).all()
    today = datetime.date.today().isoformat()

    if request.method == "POST":
        vendor_id_raw = request.form.get("vendor_id", "")

        if vendor_id_raw == "new":
            new_name = request.form.get("new_vendor_name", "").strip()
            if not new_name:
                flash("Please enter a name for the new vendor.", "error")
                return render_template("expenses/new.html", vendors=vendors, ato_categories=ATO_CATEGORIES, today=today)
            vendor = Vendor(
                name=new_name,
                default_currency=request.form.get("new_vendor_currency", "AUD"),
                ato_category=request.form.get("new_vendor_ato_category", ATO_CATEGORIES[0]),
                charges_gst=bool(request.form.get("new_vendor_charges_gst")),
                api_available=False,
                sync_frequency="on_demand",
                pdf_required=bool(request.form.get("new_vendor_pdf_required")),
            )
            db.session.add(vendor)
            db.session.flush()
        else:
            try:
                vendor = Vendor.query.get_or_404(int(vendor_id_raw))
            except (ValueError, TypeError):
                flash("Please select a vendor.", "error")
                return render_template("expenses/new.html", vendors=vendors, ato_categories=ATO_CATEGORIES, today=today)

        try:
            invoice_date = datetime.date.fromisoformat(request.form["invoice_date"])
            amount_original = Decimal(request.form["amount_original"])
            currency = request.form["currency"].upper().strip()
            ato_category = request.form["ato_category"]
            invoice_number = request.form.get("invoice_number", "").strip() or None
            description = request.form.get("description", "").strip() or None
            notes = request.form.get("notes", "").strip() or None
            gst_amount_str = request.form.get("gst_amount", "").strip()
            gst_amount = Decimal(gst_amount_str) if gst_amount_str else None
        except (ValueError, InvalidOperation) as e:
            flash(f"Invalid form data: {e}", "error")
            return render_template("expenses/new.html", vendors=vendors, ato_categories=ATO_CATEGORIES, today=today)

        # File under the FY the invoice belongs to, not the FY we happen to be in today
        fy = FinancialYear.get_or_create_for_date(invoice_date)
        manual_rate_str = request.form.get("manual_rate", "").strip()
        amount_aud = amount_original
        rba_rate = None

        if currency != "AUD":
            if manual_rate_str:
                try:
                    manual_rate = Decimal(manual_rate_str)
                    amount_aud, rba_rate = CurrencyConverter().manual_override(amount_original, manual_rate)
                except InvalidOperation:
                    flash("Invalid manual rate. Please enter a valid number.", "error")
                    return render_template("expenses/new.html", vendors=vendors, ato_categories=ATO_CATEGORIES, today=today)
            else:
                try:
                    amount_aud, rba_rate = CurrencyConverter().convert(amount_original, currency, invoice_date)
                except RBAClientError as e:
                    flash(
                        f"Could not fetch exchange rate: {e} — please enter the RBA rate manually.",
                        "error",
                    )
                    return render_template("expenses/new.html", vendors=vendors, ato_categories=ATO_CATEGORIES, today=today)

        # Read optional invoice attachment
        invoice_file = request.files.get("invoice_file")
        pdf_bytes = None
        if invoice_file and invoice_file.filename:
            pdf_bytes = invoice_file.read() or None

        expense = Expense(
            vendor_id=vendor.id,
            financial_year_id=fy.id,
            invoice_date=invoice_date,
            amount_original=amount_original,
            currency=currency,
            rba_rate=rba_rate,
            amount_aud=amount_aud,
            gst_amount=gst_amount,
            ato_category=ato_category,
            invoice_number=invoice_number,
            description=description,
            notes=notes,
            pdf_data=pdf_bytes,
            invoice_attached=bool(pdf_bytes),
            source=ExpenseSource.manual,
        )
        db.session.add(expense)
        db.session.commit()

        flash(f"Expense saved — ${amount_aud:,.2f} AUD ({vendor.name}, {invoice_date}).")
        return redirect(url_for("expenses.detail", expense_id=expense.id))

    return render_template("expenses/new.html", vendors=vendors, ato_categories=ATO_CATEGORIES, today=today)


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
    """Stream the stored invoice attachment (PDF or image) for an expense."""
    expense = Expense.query.get_or_404(expense_id)
    if not expense.pdf_data:
        abort(404)
    mimetype, ext = _detect_mimetype(expense.pdf_data)
    return send_file(
        io.BytesIO(expense.pdf_data),
        mimetype=mimetype,
        download_name=f"invoice-{expense_id}{ext}",
    )
