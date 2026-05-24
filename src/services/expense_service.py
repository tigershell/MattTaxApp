import datetime
from typing import List
from ..extensions import db
from ..models.document import Document
from ..models.expense import Expense


class ExpenseService:
    """CRUD operations for expenses and their linked documents."""

    def create(self, form_data: dict, pdf_bytes: bytes, filename: str) -> Expense:
        """Save a Document then an Expense linked to it."""
        doc = Document(filename=filename, data=pdf_bytes)
        db.session.add(doc)
        db.session.flush()

        expense = Expense(
            vendor=form_data["vendor"],
            invoice_date=datetime.date.fromisoformat(form_data["invoice_date"]),
            amount_aud=form_data["amount_aud"],
            ato_category=form_data["ato_category"],
            description=form_data.get("description"),
            notes=form_data.get("notes"),
            document_id=doc.id,
        )
        db.session.add(expense)
        db.session.commit()
        return expense

    def get_all(self) -> List[Expense]:
        return Expense.query.order_by(Expense.invoice_date.desc()).all()

    def get_by_id(self, expense_id: int) -> Expense:
        return Expense.query.get_or_404(expense_id)

    def update(self, expense_id: int, form_data: dict) -> Expense:
        expense = self.get_by_id(expense_id)
        expense.vendor = form_data["vendor"]
        expense.invoice_date = datetime.date.fromisoformat(form_data["invoice_date"])
        expense.amount_aud = form_data["amount_aud"]
        expense.ato_category = form_data["ato_category"]
        expense.description = form_data.get("description")
        expense.notes = form_data.get("notes")
        db.session.commit()
        return expense

    def delete(self, expense_id: int) -> None:
        expense = self.get_by_id(expense_id)
        db.session.delete(expense)
        db.session.commit()
