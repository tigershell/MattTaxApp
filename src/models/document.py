from ..extensions import db
import datetime


class Document(db.Model):
    """Stores raw PDF bytes for a tax invoice."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(50), default="application/pdf")
    data = db.Column(db.LargeBinary, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
