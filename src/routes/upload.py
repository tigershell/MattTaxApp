import os
import re
import tempfile
import datetime
import logging
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required

from ..extensions import db
from ..models.expense import Expense, ExpenseSource, ATO_CATEGORIES
from ..models.vendor import Vendor
from ..models.financial_year import FinancialYear
from ..api_clients.pdf_extractor import PDFExtractor
from ..logic.currency_converter import CurrencyConverter
from ..logic.duplicate_detector import DuplicateDetector
from ..api_clients.rba_client import RBAClientError

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)


def _tokenize(text: str) -> set[str]:
    """Split a vendor name into lowercase alphanumeric tokens, min 3 chars."""
    return {t for t in re.split(r'[^a-z0-9]+', text.lower()) if len(t) >= 3}


def _match_vendor(extracted_name: str | None) -> int | None:
    """Try to find a Vendor whose name appears in the extracted vendor string.

    First tries a substring match, then falls back to token overlap so that
    legal names like 'fal - Features & Labels, Inc.' still match 'Fal.ai'.
    Returns the vendor id of the best match, or None if no match found.
    """
    if not extracted_name:
        return None
    name_lower = extracted_name.lower()
    extracted_tokens = _tokenize(extracted_name)
    logger.info("Vendor matching: extracted=%r tokens=%s", extracted_name, extracted_tokens)
    vendors = Vendor.query.all()
    for vendor in vendors:
        vendor_lower = vendor.name.lower()
        if vendor_lower in name_lower or name_lower in vendor_lower:
            logger.info("Vendor matched (substring): %s", vendor.name)
            return vendor.id
        if _tokenize(vendor.name) & extracted_tokens:
            logger.info("Vendor matched (token): %s", vendor.name)
            return vendor.id
    logger.info("No vendor match found for %r", extracted_name)
    return None


@upload_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Step 1: receive PDF, extract data, show confirmation form."""
    vendors = Vendor.query.order_by(Vendor.name).all()

    if request.method == "POST":
        pdf_file = request.files.get("invoice")
        if not pdf_file or not pdf_file.filename.lower().endswith(".pdf"):
            flash("Please upload a PDF file.", "error")
            return redirect(url_for("upload.upload"))

        pdf_bytes = pdf_file.read()
        if len(pdf_bytes) == 0:
            flash("The uploaded file is empty.", "error")
            return redirect(url_for("upload.upload"))

        # Write PDF to a temp file so we can retrieve it at the confirm step
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(pdf_bytes)
        tmp.close()
        session["pending_pdf_path"] = tmp.name
        session["pending_filename"] = pdf_file.filename

        # Extract structured data from the PDF
        extracted = {}
        extraction_error = None
        try:
            extractor = PDFExtractor(api_key=os.getenv("ANTHROPIC_API_KEY"))
            extracted = extractor.extract(pdf_bytes)
            if not extracted:
                extraction_error = "Claude could not extract data from this PDF. Please fill in the fields manually."
        except Exception as e:
            logger.error("PDF extraction failed: %s", e)
            extraction_error = f"Extraction error: {e}. Please fill in the fields manually."

        if extraction_error:
            flash(extraction_error, "error")

        matched_vendor_id = _match_vendor(extracted.get("vendor"))

        return render_template(
            "upload/confirm.html",
            extracted=extracted,
            filename=pdf_file.filename,
            vendors=vendors,
            ato_categories=ATO_CATEGORIES,
            matched_vendor_id=matched_vendor_id,
        )

    return render_template("upload/index.html", vendors=vendors)


@upload_bp.route("/upload/confirm", methods=["POST"])
@login_required
def confirm():
    """Step 2: user has reviewed the extracted data — save the expense."""
    pdf_path = session.pop("pending_pdf_path", None)
    filename = session.pop("pending_filename", "invoice.pdf")

    # Read and clean up the temp PDF file
    pdf_bytes = None
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        os.unlink(pdf_path)

    # Parse form values
    try:
        vendor_id_raw = request.form["vendor_id"]
        invoice_date = datetime.date.fromisoformat(request.form["invoice_date"])
        amount_original = Decimal(request.form["amount_original"])
        currency = request.form["currency"].upper().strip()
        ato_category = request.form["ato_category"]
        description = request.form.get("description", "").strip() or None
        notes = request.form.get("notes", "").strip() or None
        gst_amount_str = request.form.get("gst_amount", "").strip()
        gst_amount = Decimal(gst_amount_str) if gst_amount_str else None
    except (ValueError, InvalidOperation) as e:
        flash(f"Invalid form data: {e}", "error")
        return redirect(url_for("upload.upload"))

    # Create a new vendor if requested
    if vendor_id_raw == "new":
        new_name = request.form.get("new_vendor_name", "").strip()
        if not new_name:
            flash("Please enter a name for the new vendor.", "error")
            return redirect(url_for("upload.upload"))
        vendor = Vendor(
            name=new_name,
            default_currency=request.form.get("new_vendor_currency", currency),
            ato_category=request.form.get("new_vendor_ato_category", ato_category),
            charges_gst=bool(request.form.get("new_vendor_charges_gst")),
            api_available=False,
            sync_frequency="on_demand",
            pdf_required=True,
        )
        db.session.add(vendor)
        db.session.flush()  # get vendor.id without committing yet
        logger.info("New vendor created: %s", vendor.name)
    else:
        try:
            vendor_id = int(vendor_id_raw)
        except ValueError:
            flash("Please select a vendor.", "error")
            return redirect(url_for("upload.upload"))
        vendor = Vendor.query.get_or_404(vendor_id)
    fy = FinancialYear.get_or_create_current()

    # Convert currency to AUD
    manual_rate_str = request.form.get("manual_rate", "").strip()
    amount_aud = amount_original
    rba_rate = None

    if currency != "AUD":
        if manual_rate_str:
            # User supplied a manual rate (API was unavailable)
            try:
                manual_rate = Decimal(manual_rate_str)
                amount_aud, rba_rate = CurrencyConverter().manual_override(amount_original, manual_rate)
            except InvalidOperation:
                flash("Invalid manual rate. Please enter a valid number.", "error")
                return redirect(url_for("upload.upload"))
        else:
            try:
                converter = CurrencyConverter()
                amount_aud, rba_rate = converter.convert(amount_original, currency, invoice_date)
            except RBAClientError as e:
                flash(
                    f"Could not fetch exchange rate: {e} — "
                    "Please enter the RBA rate manually in the form.",
                    "error",
                )
                return redirect(url_for("upload.upload"))

    # Check for duplicates
    detector = DuplicateDetector()
    existing = detector.find_match(vendor.id, invoice_date, amount_aud)

    if existing:
        if existing.invoice_attached:
            flash(
                f"Duplicate invoice — this already exists as Expense #{existing.id} "
                f"({existing.vendor.name}, {existing.formatted_date()}). No changes made.",
                "error",
            )
            return redirect(url_for("expenses.detail", expense_id=existing.id))
        # Existing record has no PDF yet — attach it now
        if pdf_bytes:
            existing.pdf_data = pdf_bytes
            existing.invoice_attached = True
            db.session.commit()
        flash(
            f"PDF attached to existing Expense #{existing.id} "
            f"({existing.vendor.name}, {existing.formatted_date()})."
        )
        return redirect(url_for("expenses.detail", expense_id=existing.id))

    # Create new expense record
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
        description=description,
        notes=notes,
        pdf_data=pdf_bytes,
        invoice_attached=bool(pdf_bytes),
        source=ExpenseSource.pdf_upload,
    )
    db.session.add(expense)
    db.session.commit()

    flash(f"Expense saved — ${amount_aud:,.2f} AUD ({vendor.name}, {invoice_date}).")
    return redirect(url_for("expenses.detail", expense_id=expense.id))