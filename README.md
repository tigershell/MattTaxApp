# Tax Tracker

A locally-deployed Flask web application for tracking Australian sole trader business expenses and income for the ATO tax return.

Upload PDF tax invoices → Claude API extracts the data automatically → expenses stored in PostgreSQL → end-of-year ATO summary generated.

**Features:**
- **Expenses** — upload invoices (PDF/JPG/PNG) for automatic extraction, or enter manually; multi-currency with RBA-style conversion; duplicate detection.
- **Income** — manual entry of sales, with GST treatment driven by your GST registration date (Stripe API sync planned).
- **Tax Summary** — net profit/loss (assessable income − deductible expenses, both ex-GST), a GST/BAS position (GST collected − Input Tax Credits), and step-by-step myTax instructions.
- **Backups** — one-click database backup/restore from the **Backup** page (or `flask backup` / `flask restore` on the CLI).

## Stack

- **Flask** — web framework
- **PostgreSQL** — database (SQLite for local dev)
- **SQLAlchemy** — ORM
- **Anthropic Python SDK** — PDF data extraction via Claude API
- **Flask-Login** — single-user session auth
- **Railway** — deployment target

## Local Development

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (copy .env.example and fill in values)
# For local dev use: DATABASE_URL=sqlite:///dev.db

# 4. Initialise the database and create the admin user
flask --app "src:create_app()" shell
>>> from src.extensions import db
>>> db.create_all()
>>> from src.models.user import User
>>> u = User(email='mattacollis@gmail.com')
>>> u.set_password('yourpassword')
>>> db.session.add(u)
>>> db.session.commit()

# 5. Run
flask --app "src:create_app()" run

# During development, add --debug to auto-reload on code changes:
flask --app "src:create_app()" --debug run
```

## Backups

The database is a single SQLite file (`instance/taxidermatt.db`). Back it up from the **Backup** page in the app ("Download backup now"), or via the CLI:

```bash
flask --app "src:create_app()" backup            # timestamped copy in backups/
flask --app "src:create_app()" restore <file>    # restore (snapshots current DB first)
```

Backups are written to `backups/` (gitignored). Keep at least one copy off this drive — they contain real financial data and invoice PDFs.

## Deployment

See `docs/tax-tracker-brief.md` for Railway deployment steps.

## Financial Year

2025–26 (1 July 2025 – 30 June 2026)