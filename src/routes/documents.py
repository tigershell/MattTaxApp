from flask import Blueprint, Response
from flask_login import login_required
from ..models.document import Document

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/documents/<int:doc_id>")
@login_required
def serve(doc_id: int):
    doc = Document.query.get_or_404(doc_id)
    return Response(doc.data, mimetype=doc.content_type)
