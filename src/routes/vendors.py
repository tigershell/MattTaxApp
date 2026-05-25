from flask import Blueprint, render_template
from flask_login import login_required

vendors_bp = Blueprint("vendors", __name__)


@vendors_bp.route("/vendors")
@login_required
def list_vendors():
    """List all configured vendors — placeholder until M1."""
    return render_template("vendors/list.html", vendors=[])
