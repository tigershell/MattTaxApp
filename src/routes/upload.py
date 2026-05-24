import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required
from ..services.pdf_extractor import PDFExtractor
from ..services.expense_service import ExpenseService
from ..models.expense import ATO_CATEGORIES

upload_bp = Blueprint("upload", __name__)
_expense_service = ExpenseService()


@upload_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        pdf_file = request.files.get("invoice")
        if not pdf_file or not pdf_file.filename.endswith(".pdf"):
            flash("Please upload a PDF file.")
            return redirect(url_for("upload.upload"))

        pdf_bytes = pdf_file.read()
        extractor = PDFExtractor(api_key=os.getenv("ANTHROPIC_API_KEY"))
        extracted = extractor.extract(pdf_bytes)

        session["pending_pdf_bytes"] = pdf_bytes.hex()
        session["pending_filename"] = pdf_file.filename

        return render_template(
            "upload/confirm.html",
            extracted=extracted,
            filename=pdf_file.filename,
            categories=ATO_CATEGORIES,
        )
    return render_template("upload/index.html")


@upload_bp.route("/upload/confirm", methods=["POST"])
@login_required
def confirm():
    pdf_bytes = bytes.fromhex(session.pop("pending_pdf_bytes", ""))
    filename = session.pop("pending_filename", "invoice.pdf")
    expense = _expense_service.create(request.form, pdf_bytes, filename)
    flash("Expense saved.")
    return redirect(url_for("expenses.detail", expense_id=expense.id))
