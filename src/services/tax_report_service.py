from decimal import Decimal

from ..models.expense import Expense, ATO_CATEGORIES
from ..models.income import Income
from ..models.financial_year import FinancialYear


class TaxReportService:
    """Generates the ATO tax summary from stored income and expenses.

    Produces three views for the current financial year:
      * Income tax — assessable income (ex-GST) minus deductible expenses
        (ex-GST), giving a net profit or loss.
      * GST / BAS — GST collected on sales minus GST paid on purchases
        (Input Tax Credits), giving the net amount owed to or refundable
        from the ATO.
      * myTax instructions — step-by-step guidance reflecting the real figures.

    All GST splitting is driven by each record's own gst_applies() check, which
    reuses the financial year's GST registration date. Pre-registration records
    are treated as GST-free automatically.
    """

    def generate_summary(self) -> dict:
        """Build the full summary dict for the current financial year."""
        fy = FinancialYear.get_or_create_current()

        expenses = (
            Expense.query
            .filter_by(financial_year_id=fy.id)
            .order_by(Expense.invoice_date)
            .all()
        )
        income_records = (
            Income.query
            .filter_by(financial_year_id=fy.id)
            .order_by(Income.received_date)
            .all()
        )

        categories, total_deductions = self._group_expenses(expenses)

        # Income tax figures — use the assessable (ex-GST) portion of income.
        gross_income = sum((Decimal(str(i.amount_aud)) for i in income_records), Decimal("0.00"))
        total_assessable_income = sum((i.assessable_amount() for i in income_records), Decimal("0.00"))
        net_position = total_assessable_income - total_deductions  # +profit / -loss

        # GST / BAS figures — output tax collected vs input tax credits paid.
        gst_collected = sum((i.gst_payable() for i in income_records), Decimal("0.00"))
        gst_paid = sum((self._expense_itc(e) for e in expenses), Decimal("0.00"))
        gst_net = gst_collected - gst_paid  # +owe ATO / -refund

        return {
            "financial_year": fy.label,
            "gst_registered": fy.gst_registration_date is not None,
            "gst_registration_date": fy.gst_registration_date,
            # Expenses
            "categories": categories,
            "total_deductions": total_deductions,
            "expense_count": len(expenses),
            # Income
            "income_records": income_records,
            "income_count": len(income_records),
            "gross_income": gross_income,
            "total_assessable_income": total_assessable_income,
            # Net income-tax position
            "net_position": net_position,
            "is_profit": net_position >= 0,
            # GST / BAS position
            "gst_collected": gst_collected,
            "gst_paid": gst_paid,
            "gst_net": gst_net,
            # Guidance
            "ato_instructions": self._build_instructions(
                total_assessable_income, total_deductions, net_position
            ),
        }

    def _group_expenses(self, expenses: list) -> tuple[dict, Decimal]:
        """Group expenses by ATO category using the deductible (ex-GST) amount.

        Returns the category map and the grand total of deductions. Once GST is
        registered, deductible_amount() excludes the GST portion (it is claimed
        as an Input Tax Credit on the BAS instead, not as an income tax
        deduction).
        """
        categories = {cat: {"expenses": [], "total": Decimal("0.00")} for cat in ATO_CATEGORIES}
        for expense in expenses:
            cat = expense.ato_category if expense.ato_category in categories else "Other Business Expenses"
            categories[cat]["expenses"].append(expense)
            categories[cat]["total"] += expense.deductible_amount()

        total = sum((v["total"] for v in categories.values()), Decimal("0.00"))
        return categories, total

    @staticmethod
    def _expense_itc(expense: Expense) -> Decimal:
        """Return the claimable GST (Input Tax Credit) for an expense, or zero."""
        if expense.gst_applies() and expense.gst_amount:
            return Decimal(str(expense.gst_amount))
        return Decimal("0.00")

    @staticmethod
    def _build_instructions(income: Decimal, deductions: Decimal, net: Decimal) -> list:
        """Build myTax instructions reflecting the real income and result."""
        income_s = f"${income:,.2f}"
        ded_s = f"${deductions:,.2f}"
        net_abs = f"${abs(net):,.2f}"

        lines = [
            "In myTax → 'Business and professional items' section:",
            "1. Did you run a business? → Yes",
            "2. Type of business: Software development / IT services",
            f"3. Business income (total assessable, ex-GST): {income_s}",
            f"4. Other expenses (total deductions, ex-GST): {ded_s}",
        ]
        if net >= 0:
            lines.append(
                f"5. Net income from business: {net_abs} (a profit) — added to your assessable income."
            )
        else:
            lines.append(f"5. Net loss from business: {net_abs} (a loss)")
            lines.append(
                "6. Non-commercial losses: Select 'Loss is not from a primary production business' "
                "— the ATO will carry it forward automatically."
            )
            lines.append(
                "7. Losses carried forward: The ATO tracks this; it appears in your account the following year."
            )
        lines.append(
            "Note: GST collected and Input Tax Credits are reported separately on your BAS, not in myTax."
        )
        return lines
