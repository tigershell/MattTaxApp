from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from ..extensions import db
from ..models.vendor import Vendor
from ..models.expense import Expense, ATO_CATEGORIES
from ..models.financial_year import FinancialYear

vendors_bp = Blueprint("vendors", __name__)


@vendors_bp.route("/vendors")
@login_required
def list_vendors():
    """List all configured vendors."""
    vendors = Vendor.query.order_by(Vendor.name).all()
    return render_template("vendors/list.html", vendors=vendors)


@vendors_bp.route("/vendors/<int:vendor_id>")
@login_required
def vendor_detail(vendor_id: int):
    """Show a vendor and all their expenses, with a total."""
    vendor = Vendor.query.get_or_404(vendor_id)
    expenses = (
        Expense.query
        .filter_by(vendor_id=vendor_id)
        .order_by(Expense.invoice_date.desc())
        .all()
    )
    total_aud = sum(Decimal(str(e.amount_aud)) for e in expenses)
    return render_template(
        "vendors/detail.html",
        vendor=vendor,
        expenses=expenses,
        total_aud=total_aud,
    )


@vendors_bp.route("/vendors/new", methods=["GET", "POST"])
@login_required
def new_vendor():
    """Create a new vendor from scratch."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Vendor name is required.", "error")
            return render_template("vendors/new.html", ato_categories=ATO_CATEGORIES)
        if Vendor.query.filter_by(name=name).first():
            flash(f"A vendor named '{name}' already exists.", "error")
            return render_template("vendors/new.html", ato_categories=ATO_CATEGORIES)
        vendor = Vendor(
            name=name,
            default_currency=request.form.get("default_currency", "AUD"),
            ato_category=request.form.get("ato_category", ATO_CATEGORIES[0]),
            charges_gst="charges_gst" in request.form,
            api_available=False,
            sync_frequency=request.form.get("sync_frequency", "on_demand"),
            pdf_required="pdf_required" in request.form,
            billing_url=request.form.get("billing_url", "").strip() or None,
            notes=request.form.get("notes", "").strip() or None,
        )
        db.session.add(vendor)
        db.session.commit()
        flash(f"Vendor '{vendor.name}' created.")
        return redirect(url_for("vendors.vendor_detail", vendor_id=vendor.id))

    return render_template("vendors/new.html", ato_categories=ATO_CATEGORIES)


@vendors_bp.route("/vendors/<int:vendor_id>/edit", methods=["GET", "POST"])
@login_required
def edit_vendor(vendor_id: int):
    """Edit a vendor's configuration."""
    vendor = Vendor.query.get_or_404(vendor_id)

    if request.method == "POST":
        vendor.default_currency = request.form["default_currency"]
        vendor.charges_gst = "charges_gst" in request.form
        vendor.ato_category = request.form["ato_category"]
        vendor.sync_frequency = request.form["sync_frequency"]
        vendor.pdf_required = "pdf_required" in request.form
        vendor.billing_url = request.form.get("billing_url", "").strip() or None
        vendor.notes = request.form.get("notes", "").strip() or None
        db.session.commit()
        flash(f"{vendor.name} updated.")
        return redirect(url_for("vendors.list_vendors"))

    return render_template(
        "vendors/edit.html",
        vendor=vendor,
        ato_categories=ATO_CATEGORIES,
    )
