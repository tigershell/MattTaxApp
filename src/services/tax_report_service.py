from decimal import Decimal
from ..models.expense import Expense, ATO_CATEGORIES


class TaxReportService:
    """Generates the ATO tax summary from stored expenses."""

    FINANCIAL_YEAR = "2025-26"

    ATO_INSTRUCTIONS = [
        "In myTax → 'Business and professional items' section:",
        "1. Did you run a business? → Yes",
        "2. Type of business: Software development / IT services",
        "3. Business income (total business income): $0.00",
        "4. Other expenses: ${grand_total} ← this is where all expenses go",
        "5. Total business deductions: ${grand_total}",
        "6. Net income or loss from business: –${grand_total} (a loss)",
        "7. Non-commercial losses: Select 'Loss is not from a primary production business' — the ATO will carry it forward automatically.",
        "8. Losses carried forward: The ATO will track this. It appears in your account the following year.",
    ]

    def generate_summary(self) -> dict:
        expenses = Expense.query.order_by(Expense.invoice_date).all()
        categories = {cat: {"expenses": [], "total": Decimal("0.00")} for cat in ATO_CATEGORIES}

        for expense in expenses:
            cat = expense.ato_category
            if cat not in categories:
                cat = "Other Business Expenses"
            categories[cat]["expenses"].append(expense)
            categories[cat]["total"] += Decimal(str(expense.amount_aud))

        grand_total = sum(v["total"] for v in categories.values())

        instructions = [
            line.replace("{grand_total}", f"{grand_total:,.2f}")
            for line in self.ATO_INSTRUCTIONS
        ]

        return {
            "categories": categories,
            "grand_total": grand_total,
            "expense_count": len(expenses),
            "financial_year": self.FINANCIAL_YEAR,
            "ato_instructions": instructions,
        }
