# Tax Tracker — Full Project Brief
*Hand this document to Claude (Coding skill) to build the app from scratch.*

---

## What We're Building

A locally-deployed Flask web application that helps an Australian sole trader (developer, no GST registration) track business expenses for their ATO tax return. The user uploads PDF tax invoices, Claude API extracts the key details automatically, and the app stores everything in a PostgreSQL database with the original PDF linked to each record. At the end of the financial year, the app generates a summary of exactly what to enter in the ATO myTax online return.

---

## User Context (Important for Tax Logic)

- **Name:** Matt
- **Country:** Australia
- **Financial year:** 2025–26 (1 July 2025 – 30 June 2026)
- **Tax situation:** Individual with full-time employment income (auto-populated by ATO) + sole trader business activity as a developer
- **GST:** NOT registered for GST — all expense amounts are fully deductible as-is, no GST component to separate
- **Business income:** $0 (starting out, no revenue yet)
- **Business losses:** Will be quarantined and carried forward under the ATO's non-commercial loss rules — they cannot be offset against salary income this year
- **Expense types:** Tax invoices only (not bank statements) — clean, structured PDFs

**Typical expense categories:**
- Domain name registrations
- Trademark filing charges (IP Australia)
- Hosting (Railway, Netlify)
- AI/API costs (Anthropic, OpenAI, fal.ai)

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Web framework | **Flask** | Lightweight, familiar, perfect for a personal tool |
| Database | **PostgreSQL** | Required for Railway deployment (SQLite is ephemeral on Railway) |
| ORM | **SQLAlchemy** | Clean ORM, works well with Flask |
| DB adapter | **psycopg2-binary** | PostgreSQL driver for Python |
| PDF extraction | **Anthropic Python SDK** | Claude API reads PDFs via base64, extracts structured data |
| Auth | **Flask-Login** | Simple session-based login to protect the deployed app |
| Password hashing | **Werkzeug** (bundled with Flask) | Already available, no extra dependency |
| Config/secrets | **python-dotenv** | .env file for API keys and DB URL |
| WSGI server | **Gunicorn** | Required for Railway deployment |
| Testing | **pytest** | Standard |

**No frontend framework** — plain HTML + minimal CSS (keep it functional, not pretty).

---

## Deployment Target

**Railway** (the user already has an account — it's one of their tax deductions).

- The Flask app is deployed as a Railway service
- PostgreSQL is provisioned as a Railway plugin (one click)
- Environment variables set in Railway dashboard
- Access from any device via the Railway-provided URL
- Protected by login (single user — Matt)

---

## Database Schema

### `users` table
```sql
id          SERIAL PRIMARY KEY
email       VARCHAR(255) UNIQUE NOT NULL
password_hash VARCHAR(255) NOT NULL
created_at  TIMESTAMP DEFAULT NOW()
```

### `documents` table
```sql
id          SERIAL PRIMARY KEY
filename    VARCHAR(255) NOT NULL
content_type VARCHAR(50) DEFAULT 'application/pdf'
data        BYTEA NOT NULL        -- PDF stored as binary blob
uploaded_at TIMESTAMP DEFAULT NOW()
```

### `expenses` table
```sql
id           SERIAL PRIMARY KEY
vendor       VARCHAR(255) NOT NULL      -- e.g. "Anthropic", "Netlify"
invoice_date DATE NOT NULL
amount_aud   NUMERIC(10, 2) NOT NULL    -- Full AUD amount (no GST split needed)
ato_category VARCHAR(100) NOT NULL      -- See ATO categories below
description  TEXT                       -- Auto-extracted or user-entered
notes        TEXT                       -- Optional user notes
document_id  INTEGER REFERENCES documents(id) ON DELETE SET NULL
created_at   TIMESTAMP DEFAULT NOW()
updated_at   TIMESTAMP DEFAULT NOW()
```

**ATO category values (use these exact strings as the enum/choices):**
- `Software & Subscriptions` — AI APIs, SaaS tools
- `Domain & Hosting` — domain registrations, Railway, Netlify
- `Legal & Professional` — trademark filings, IP Australia fees
- `Other Business Expenses` — anything else

These all flow into "Other expenses" in the myTax business schedule, but keeping them categorised makes the summary more useful.

---

## Class Structure

### `src/models/user.py`
```
User (db.Model, UserMixin)
  - id, email, password_hash, created_at
  - check_password(password) → bool
  - set_password(password) → None
```

### `src/models/document.py`
```
Document (db.Model)
  - id, filename, content_type, data, uploaded_at
  - No special methods — data access only
```

### `src/models/expense.py`
```
Expense (db.Model)
  - id, vendor, invoice_date, amount_aud, ato_category,
    description, notes, document_id, created_at, updated_at
  - document (relationship → Document)
  - formatted_amount() → "$1,234.56"
  - formatted_date() → "15 Jan 2026"
```

### `src/services/pdf_extractor.py`
```
PDFExtractor
  - __init__(api_key: str)
  - extract(pdf_bytes: bytes) → dict
      Sends PDF to Claude API (base64-encoded) with a structured prompt.
      Returns: {
        "vendor": str,
        "invoice_date": str (YYYY-MM-DD),
        "amount_aud": float,
        "ato_category": str,
        "description": str
      }
      Falls back gracefully if extraction fails (returns empty dict).
```

**Claude API prompt for extraction (use this exactly):**
```
You are extracting data from an Australian business tax invoice.
Return ONLY a JSON object with these exact keys:
- vendor: the company or supplier name
- invoice_date: the invoice date in YYYY-MM-DD format
- amount_aud: the total amount in AUD as a number (no currency symbol)
- ato_category: one of exactly these values: "Software & Subscriptions", "Domain & Hosting", "Legal & Professional", "Other Business Expenses"
- description: a brief description of what was purchased (max 100 chars)

If you cannot determine a value with confidence, use null.
Return only valid JSON, no explanation.
```

### `src/services/expense_service.py`
```
ExpenseService
  - create(form_data: dict, pdf_bytes: bytes, filename: str) → Expense
      Saves Document then Expense, links them.
  - get_all() → List[Expense] (ordered by invoice_date DESC)
  - get_by_id(id: int) → Expense
  - update(id: int, form_data: dict) → Expense
  - delete(id: int) → None
```

### `src/services/tax_report_service.py`
```
TaxReportService
  - generate_summary() → dict
      Returns: {
        "categories": {category: {"expenses": [...], "total": Decimal}},
        "grand_total": Decimal,
        "expense_count": int,
        "financial_year": "2025-26",
        "ato_instructions": [list of plain-English field instructions]
      }
```

### `src/routes/` (Flask Blueprints)

- `auth.py` — `/login`, `/logout`
- `expenses.py` — `/`, `/expenses/<id>`, `/expenses/<id>/edit`, `/expenses/<id>/delete`
- `upload.py` — `/upload` (GET shows form, POST processes PDF)
- `documents.py` — `/documents/<id>` (serves raw PDF bytes for inline viewing)
- `reports.py` — `/report`

---

## Folder Structure

```
tax-tracker/
├── venv/
├── src/
│   ├── __init__.py          ← app factory (create_app())
│   ├── extensions.py        ← db = SQLAlchemy(), login_manager = LoginManager()
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── expense.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py
│   │   ├── expense_service.py
│   │   └── tax_report_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── expenses.py
│   │   ├── upload.py
│   │   ├── documents.py
│   │   └── reports.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── expenses/
│       │   ├── list.html        ← homepage, table of all expenses
│       │   ├── detail.html      ← expense + inline PDF viewer
│       │   └── edit.html
│       ├── upload/
│       │   ├── index.html       ← upload form
│       │   └── confirm.html     ← pre-filled form after Claude extraction
│       └── reports/
│           └── summary.html     ← ATO tax summary
├── tests/
│   ├── test_extractor.py
│   └── test_report.py
├── docs/
│   └── tax-tracker-brief.md    ← this file
├── .env                         ← never commit
├── .gitignore
├── requirements.txt
├── Procfile                     ← web: gunicorn "src:create_app()"
└── README.md
```

---

## Data Flow

### Upload Flow
```
User selects PDF → POST /upload
  → upload route reads file bytes
    → PDFExtractor.extract(pdf_bytes)
      → Claude API (base64 PDF in message)
      ← JSON with vendor, date, amount, category, description
    ← Pre-filled HTML form (confirm.html) shown to user
  User reviews / corrects fields → POST /upload/confirm
    → ExpenseService.create(form_data, pdf_bytes, filename)
      → saves Document (PDF bytes in DB)
      → saves Expense (linked to Document)
    ← Redirect to expense detail page
```

### View PDF Flow
```
User clicks "View Invoice" on detail page
  → GET /documents/<id>
    → fetch Document.data from DB
    ← Response(bytes, mimetype='application/pdf')
  Browser renders PDF inline in <iframe>
```

### Tax Report Flow
```
User clicks "Tax Summary" → GET /report
  → TaxReportService.generate_summary()
    → queries all Expense records
    → groups by ato_category
    → sums totals
    ← dict with categories, totals, ATO instructions
  ← summary.html rendered with table + instructions
```

---

## ATO myTax Instructions (for the report page)

The report page should display these instructions verbatim, with the calculated amounts filled in:

**In myTax → "Business and professional items" section:**

1. **Did you run a business?** → Yes
2. **Type of business:** Software development / IT services
3. **Business income (total business income):** $0.00
4. **Other expenses:** $[GRAND_TOTAL] ← this is where all expenses go
5. **Total business deductions:** $[GRAND_TOTAL]
6. **Net income or loss from business:** –$[GRAND_TOTAL] (a loss)
7. **Non-commercial losses:** Because the business has no income, this loss is quarantined under the non-commercial loss rules. Select **"Loss is not from a primary production business"** and the ATO will carry it forward automatically.
8. **Losses carried forward:** The ATO will track this — you don't need to enter it manually. It appears in your account the following year.

---

## Environment Variables (.env)

```
ANTHROPIC_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=a_long_random_string_for_flask_sessions
ADMIN_EMAIL=mattacollis@gmail.com
ADMIN_PASSWORD=choose_a_strong_password
```

On Railway, these are set in the dashboard (not in a file).

---

## requirements.txt

```
flask
flask-login
flask-sqlalchemy
psycopg2-binary
anthropic
python-dotenv
gunicorn
pytest
werkzeug
```

---

## Setup Instructions (local dev)

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd tax-tracker

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (copy template above, fill in values)

# 5. For local dev, use a local PostgreSQL instance or SQLite override
# Add to .env for local: DATABASE_URL=sqlite:///dev.db

# 6. Initialise the database and create the admin user
flask --app "src:create_app()" shell
>>> from src.extensions import db
>>> db.create_all()
>>> from src.models.user import User
>>> u = User(email='mattacollis@gmail.com')
>>> u.set_password('yourpassword')
>>> db.session.add(u)
>>> db.session.commit()

# 7. Run
flask --app "src:create_app()" run
```

## Railway Deployment

1. Push code to GitHub
2. Create new Railway project → Deploy from GitHub repo
3. Add PostgreSQL plugin → copy DATABASE_URL to environment variables
4. Set all environment variables in Railway dashboard
5. Railway auto-detects Procfile and deploys

---

## Build Order (for Claude to follow)

Build in this exact sequence — test each step before moving to the next:

1. **Project scaffold** — folder structure, `__init__.py`, `extensions.py`, `create_app()` factory, `.env`, `requirements.txt`, `.gitignore`
2. **Models** — `User`, `Document`, `Expense` with SQLAlchemy, `db.create_all()`
3. **Auth** — login/logout routes, `Flask-Login` integration, login template, protect all routes with `@login_required`
4. **Expense list page** — `/` route, `expenses/list.html`, empty state when no expenses yet
5. **PDF upload + Claude extraction** — `PDFExtractor`, upload form, confirm form, `ExpenseService.create()`
6. **Expense detail page** — `/expenses/<id>`, inline PDF viewer via `<iframe>`, edit/delete
7. **Tax report** — `TaxReportService`, `/report`, `summary.html` with ATO instructions
8. **Polish** — sensible error handling throughout, flash messages, loading state on upload (Claude extraction takes a few seconds)
9. **Deploy to Railway** — `Procfile`, test in production

---

## Key Design Decisions

- **PDFs stored as BYTEA in PostgreSQL** — keeps everything in one place, no S3/R2 needed, perfectly fine for ~100 invoices/year
- **Claude API used only at upload time** — extract once, store the structured data. No repeated API calls.
- **Base64 encoding for PDF → Claude** — simpler than the Files API for a one-shot extraction workflow
- **Single user** — no multi-tenancy needed. One user record created at setup, login protects the app.
- **No GST handling** — Matt is not GST registered. The full invoice amount is the deductible amount. No GST column needed.
- **SQLite for local dev** — use `DATABASE_URL=sqlite:///dev.db` in local `.env` to avoid needing a local Postgres instance during development. SQLAlchemy handles both transparently.
