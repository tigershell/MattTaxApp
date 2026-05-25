from flask import Blueprint, render_template
from flask_login import login_required

years_bp = Blueprint("years", __name__)


@years_bp.route("/years")
@login_required
def list_years():
    """List financial years — placeholder until M1."""
    return render_template("years/list.html", years=[])
