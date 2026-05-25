# Architecture — Taxidermatt

*Completed: 25 May 2026*
*Next stage: Project Manager*

---

## MCP Integration Decisions

**Assessment:** This app calls three external APIs (Railway GraphQL, RBA Exchange Rate, Anthropic SDK). Before finalising the API-direct approach, MCPs were evaluated.

- **Railway MCP:** No production-grade MCP found for Railway billing data. Railway's API is niche enough that no widely-adopted MCP exists. Build direct GraphQL calls.
- **RBA Exchange Rate MCP:** No MCP found. A direct REST call to exchangeratesapi.com.au is trivially simple and appropriate.
- **Anthropic MCP:** The Anthropic SDK is used directly for PDF extraction — routing through an MCP layer would add unnecessary indirection. SDK direct.

**Decision:** All external integrations are built as direct API calls inside dedicated client classes. No MCPs consumed.

Note: `a2asearch-mcp` was not available in this environment. This assessment was made via web research. Revisit if MCPs for Railway or RBA emerge during the build.

---

## API Capability Verification

### Railway GraphQL API

**Endpoint:** `POST https://backboard.railway.com/graphql/v2`
**Auth:** `Authorization: Bearer {RAILWAY_API_KEY}` (Account Token required for billing scope)

**Confirmed:**
- The API is the same one powering the Railway dashboard — billing data is definitively accessible via GraphQL.
- The schema is fully introspectable via the GraphiQL playground at `railway.com/graphiql`.
- A `billing` namespace exists in the schema covering subscriptions, usage limits, and charges.

**Critical caveat:** Billing queries are **not formally documented** in Railway's public docs. The exact query name for invoice history (likely `usageForSubscription` or similar) must be confirmed by introspecting the live schema with a Railway API key. This is the first task in the coding stage.

**Limitations to design around:**
- No guaranteed SLA on billing API stability (flagged in the product design brief).
- Exact field names unknown until introspection. `RailwayClient` is isolated so it can be updated without touching the rest of the app.
- Data returned is likely compute usage metrics (vCPU/min, GB/min, network) aggregated into invoice line items — not a downloadable PDF. Railway invoices must still be downloaded manually from the dashboard.

**ATO implication:** Railway invoices need PDFs attached for ATO substantiation. The API sync creates expense records; PDF upload then attaches the invoice. This is already reflected in the product design (source=api_sync, invoice_attached=False until PDF uploaded).

### RBA Exchange Rate API (exchangeratesapi.com.au)

**Endpoint:** `GET https://api.exchangeratesapi.com.au/{YYYY-MM-DD}/{currency_code}`
**Auth:** API key via `Authorization` header (free tier, no credit card required)

**Confirmed:**
- Returns the RBA exchange rate for a specific currency on a specific historical date.
- Complete history from 2018 onwards (~30,000+ data points).
- Automatic fallback to previous business day if requested date is a weekend or public holiday (with staleness flag in response).
- Free tier: 300 requests/month.
- Not officially affiliated with or endorsed by the RBA — it is a third-party service wrapping publicly available RBA HTML/RSS data into JSON. The underlying data is the same.

**ATO note:** The ATO explicitly accepts RBA exchange rates for foreign currency conversion. This source is appropriate.

**Limitations to design around:**
- 300 calls/month free limit. All fetched rates must be cached in the `RBARate` DB table — never fetch the same date/currency pair twice.
- If the free tier is ever exhausted, fallback is direct RBA RSS parsing (free, no limit) — worth noting in `docs/api_notes.md` during coding.

### Anthropic SDK (PDF Extraction)

**Method:** `anthropic` Python SDK, `claude-opus-4-7` model, base64-encoded PDF as document content.

**Confirmed:**
- Well-documented, stable API.
- PDF extraction via base64 encoding is a supported pattern.
- One-shot extraction at upload time only — no background processing needed.
- Cost: ~$0.05–0.10 AUD per invoice, trivial for personal use.

**Limitations to design around:**
- Claude may misread low-quality PDFs or non-standard invoice layouts. The extraction result must always be shown to the user for confirmation before saving — do not auto-commit without review.
- Structured output from Claude requires a well-designed prompt. The extraction prompt is a first-class design artifact — document it in `docs/api_notes.md`.

---

## Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Web framework | Flask | Lightweight, appropriate for a personal web app. Blueprints give clean modular structure. |
| ORM | SQLAlchemy (Flask-SQLAlchemy) | Handles SQLite (dev) and PostgreSQL (prod) with identical model code. Switched via `DATABASE_URL`. |
| DB migrations | Flask-Migrate (Alembic) | Schema will evolve across versions. Migrations are non-negotiable for a production database. |
| Auth | Flask-Login | Single-user session-based authentication. Exactly the right tool. |
| Dev database | SQLite | Zero setup, runs locally. No server needed during development. |
| Prod database | PostgreSQL | Provisioned on Railway. Same SQLAlchemy models, different connection string. |
| HTTP client | requests | Railway GraphQL and RBA API calls. Simple and sufficient — no async required. |
| PDF extraction | Anthropic Python SDK | Direct SDK use. No intermediate layer. |
| Secrets | python-dotenv | `.env` file pattern. All API keys and the database URL live here. |
| Templates | Jinja2 | Included with Flask. |
| Testing | pytest | Standard Python testing. |
| Production server | Gunicorn | WSGI server for Railway deployment. |

**Not included (and why):**
- Flask-WTF: CSRF risk is low for a localhost personal tool. Add later if needed.
- Celery / background tasks: All sync is manual-trigger in v1. No background scheduler needed.
- Redis: No caching layer needed — RBA rate cache lives in the database.

---

## Class Design

### Models (SQLAlchemy — `src/models/`)

**`FinancialYear`** (`financial_year.py`)
- Responsibility: One ATO financial year (1 Jul – 30 Jun) and its GST configuration.
- Fields: `id`, `label` ("FY 2025-26"), `start_date`, `end_date`, `gst_registration_date` (nullable)
- Methods:
  - `is_gst_registered_on(date: date) -> bool` — True if GST registration date is set and date >= it
  - `current_year() -> FinancialYear` (classmethod) — returns the FY containing today's date
- Dependencies: none

**`Vendor`** (`vendor.py`)
- Responsibility: Config record for one service provider.
- Fields: `id`, `name`, `api_available` (bool), `default_currency`, `charges_gst` (bool), `ato_category`, `sync_frequency`, `notes`
- No API credentials stored in the model — keys stay in `.env`.
- Dependencies: none

**`Expense`** (`expense.py`)
- Responsibility: One invoice / expense record.
- Fields: `id`, `vendor_id` (FK), `financial_year_id` (FK), `invoice_date`, `amount_original` (Numeric), `currency`, `rba_rate` (Numeric, nullable), `amount_aud` (Numeric), `gst_amount` (Numeric, nullable), `ato_category`, `description`, `notes`, `pdf_data` (LargeBinary, nullable), `invoice_attached` (bool), `source` (Enum: api_sync / pdf_upload / manual), `created_at`
- Methods:
  - `gst_applies() -> bool` — True if vendor charges GST and the FY's GST registration date is set and invoice_date >= it
  - `deductible_amount() -> Decimal` — amount_aud minus gst_amount if GST applies, else full amount_aud
- Dependencies: `Vendor`, `FinancialYear`

**`RBARate`** (`rba_rate.py`)
- Responsibility: Cached exchange rate for one date/currency pair.
- Fields: `id`, `rate_date`, `currency_code`, `rate` (Numeric), `fetched_at`
- Purpose: Protects the 300/month API free tier. Check this table before every API call.
- Dependencies: none

---

### API Clients (`src/api_clients/`)

**`RailwayClient`** (`railway_client.py`)
- Responsibility: All GraphQL communication with the Railway API.
- Methods:
  - `get_billing_history(from_date: date, to_date: date) -> list[dict]` — returns list of invoice dicts
  - `_execute_query(query: str, variables: dict) -> dict` — executes one GraphQL request
  - `_handle_error(response: Response) -> None` — raises appropriate exception on 401, 429, 500
- Auth: `Authorization: Bearer {RAILWAY_API_KEY}` from env var
- Note: Exact billing query to be confirmed via GraphiQL during coding. Document findings in `docs/api_notes.md`.

**`RBAClient`** (`rba_client.py`)
- Responsibility: Fetch and cache exchange rates.
- Methods:
  - `get_rate(rate_date: date, currency_code: str) -> Decimal` — returns rate, hits cache first
  - `_fetch_from_api(rate_date: date, currency_code: str) -> Decimal` — calls exchangeratesapi.com.au
  - `_check_cache(rate_date: date, currency_code: str) -> Decimal | None` — queries RBARate table
  - `_save_to_cache(rate_date: date, currency_code: str, rate: Decimal) -> None`
- Dependencies: `RBARate` model

**`PDFExtractor`** (`pdf_extractor.py`)
- Responsibility: Extract structured invoice data from a PDF using Claude.
- Methods:
  - `extract(pdf_bytes: bytes) -> dict` — returns {vendor_name, invoice_date, amount, currency, gst_amount, description}
  - `_build_prompt() -> str` — returns the structured extraction prompt
  - `_encode_pdf(pdf_bytes: bytes) -> str` — base64 encodes the PDF
  - `_parse_response(content: str) -> dict` — parses Claude's response into structured dict
- Model: `claude-opus-4-7`
- Dependencies: Anthropic SDK

---

### Business Logic (`src/logic/`)

**`DuplicateDetector`** (`duplicate_detector.py`)
- Responsibility: Determine if a new record matches an existing one before creating a duplicate.
- Methods:
  - `find_match(vendor_id: int, invoice_date: date, amount: Decimal) -> Expense | None`
- Matching tolerance: ±1 day on date, ±$0.01 AUD on amount.
- Dependencies: `Expense` model

**`CurrencyConverter`** (`currency_converter.py`)
- Responsibility: Convert a foreign amount to AUD using the RBA rate for the invoice date.
- Methods:
  - `convert(amount: Decimal, currency: str, invoice_date: date) -> tuple[Decimal, Decimal]` — returns (aud_amount, rate_used)
  - `manual_override(amount: Decimal, rate: Decimal) -> Decimal` — for cases where automatic fetch fails
- Dependencies: `RBAClient`

**`TaxCalculator`** (`tax_calculator.py`)
- Responsibility: Apply Australian tax rules to a set of expenses.
- Methods:
  - `apply_gst_rules(expenses: list[Expense], gst_date: date | None) -> list[Expense]` — sets gst_amount on each record
  - `group_by_ato_category(expenses: list[Expense]) -> dict[str, list[Expense]]`
  - `total_deductible(expenses: list[Expense]) -> Decimal`
  - `total_gst_credits(expenses: list[Expense]) -> Decimal`
- No database access — operates on lists of Expense objects passed in.
- Dependencies: none (pure logic)

**`ReportGenerator`** (`report_generator.py`)
- Responsibility: Produce the final structured data for tax and BAS reports.
- Methods:
  - `tax_summary(financial_year: FinancialYear) -> dict` — {categories, totals, mytax_fields}
  - `bas_report(financial_year: FinancialYear, quarter: int) -> dict` — {gst_on_purchases, net_gst_payable}
- Dependencies: `TaxCalculator`, `Expense` model

**`SyncOrchestrator`** (`sync_orchestrator.py`)
- Responsibility: Coordinate a full Railway API sync run from end to end.
- Methods:
  - `run_railway_sync(financial_year: FinancialYear) -> SyncResult` — returns {created: int, skipped: int, errors: list}
- Sequence: RailwayClient → DuplicateDetector → CurrencyConverter → create Expense records → commit
- Dependencies: `RailwayClient`, `DuplicateDetector`, `CurrencyConverter`, `Expense`, `Vendor`

---

### Flask Blueprints (`src/routes/`)

| File | Blueprint | Routes |
|------|-----------|--------|
| `auth.py` | `auth` | GET/POST `/login`, GET `/logout` |
| `dashboard.py` | `dashboard` | GET `/` |
| `expenses.py` | `expenses` | GET `/expenses`, GET `/expenses/<id>`, POST `/expenses/upload`, POST `/expenses/sync-railway`, POST `/expenses/<id>/attach-pdf` |
| `vendors.py` | `vendors` | GET `/vendors`, GET/POST `/vendors/<id>/edit` |
| `years.py` | `years` | GET `/years`, POST `/years/<id>/set-gst-date` |
| `reports.py` | `reports` | GET `/reports/tax-summary`, GET `/reports/bas` |

---

## Folder Structure

```
F:\Pycharm Projects\MattTaxApp\
├── venv\
├── src\
│   ├── __init__.py              ← create_app() factory function
│   ├── config.py                ← DevelopmentConfig, ProductionConfig
│   ├── extensions.py            ← db, login_manager, migrate (instantiated here, attached in create_app)
│   ├── models\
│   │   ├── __init__.py
│   │   ├── financial_year.py
│   │   ├── vendor.py
│   │   ├── expense.py
│   │   └── rba_rate.py
│   ├── api_clients\
│   │   ├── __init__.py
│   │   ├── railway_client.py
│   │   ├── rba_client.py
│   │   └── pdf_extractor.py
│   ├── logic\
│   │   ├── __init__.py
│   │   ├── duplicate_detector.py
│   │   ├── currency_converter.py
│   │   ├── tax_calculator.py
│   │   ├── report_generator.py
│   │   └── sync_orchestrator.py
│   ├── routes\
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── expenses.py
│   │   ├── vendors.py
│   │   ├── years.py
│   │   └── reports.py
│   ├── templates\
│   │   ├── base.html
│   │   ├── auth\
│   │   │   └── login.html
│   │   ├── dashboard\
│   │   │   └── index.html
│   │   ├── expenses\
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   └── upload.html
│   │   ├── vendors\
│   │   │   ├── list.html
│   │   │   └── edit.html
│   │   ├── years\
│   │   │   └── list.html
│   │   └── reports\
│   │       ├── tax_summary.html
│   │       └── bas.html
│   └── static\
│       ├── css\
│       │   └── style.css        ← design system CSS variables from src/design_system.py
│       └── js\
│           └── main.js
├── tests\
│   ├── __init__.py
│   ├── test_duplicate_detector.py
│   ├── test_currency_converter.py
│   ├── test_tax_calculator.py
│   └── test_report_generator.py
├── migrations\                  ← Flask-Migrate / Alembic managed — do not edit manually
├── docs\
│   ├── product-design-brief.md
│   ├── architecture.md
│   ├── api_notes.md             ← Railway query schema findings + PDF extraction prompt
│   └── design-preview.html
├── .env                         ← never committed
├── .env.example                 ← committed with blank values
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Data Flow

### Flow 1: Railway API Sync

```
Matt clicks "Sync Railway" button
  → expenses route: POST /expenses/sync-railway
    → SyncOrchestrator.run_railway_sync(financial_year)
      → RailwayClient.get_billing_history(from_date, to_date)
        → POST backboard.railway.com/graphql/v2
        ← list of invoice dicts [{date, amount_usd, description}, ...]
      → For each invoice:
        → DuplicateDetector.find_match(vendor_id, invoice_date, amount)
        → If match found: skip (already exists)
        → If no match:
          → CurrencyConverter.convert(amount, "USD", invoice_date)
            → RBAClient.get_rate(invoice_date, "USD")
              → Check RBARate table (cache)
              → If miss: GET api.exchangeratesapi.com.au/{date}/USD
              → Save to RBARate cache
            ← rate
          ← (aud_amount, rate_used)
          → Create Expense(source=api_sync, invoice_attached=False)
      → db.session.commit()
    ← SyncResult(created=N, skipped=M, errors=[...])
  → Flash result message to dashboard
```

### Flow 2: PDF Upload

```
Matt drops a PDF onto the upload form
  → expenses route: POST /expenses/upload
    → PDFExtractor.extract(pdf_bytes)
      → Anthropic SDK: base64 PDF + extraction prompt → claude-opus-4-7
      ← {vendor_name, invoice_date, amount, currency, gst_amount, description}
    → Show extracted data to user for confirmation (do not auto-save)
    → User confirms or corrects fields → POST /expenses/upload/confirm
      → DuplicateDetector.find_match(vendor_id, invoice_date, amount)
      → If match found:
        → Attach pdf_data to existing Expense, set invoice_attached=True
      → If no match:
        → If currency != "AUD":
          → CurrencyConverter.convert(amount, currency, invoice_date)
        → Create new Expense(source=pdf_upload, invoice_attached=True, pdf_data=bytes)
      → db.session.commit()
```

### Flow 3: Tax Report

```
Matt opens Reports > ATO Tax Summary
  → reports route: GET /reports/tax-summary?year_id=X
    → Query FinancialYear by id
    → ReportGenerator.tax_summary(financial_year)
      → Query all Expense records for this FinancialYear
      → TaxCalculator.apply_gst_rules(expenses, fy.gst_registration_date)
      → TaxCalculator.group_by_ato_category(expenses)
      → TaxCalculator.total_deductible(expenses)
      ← {
           categories: {category_name: {expenses: [...], subtotal: Decimal}},
           total_deductible: Decimal,
           mytax_fields: {
             "D15 Other deductions": Decimal,
             "Income from business - net loss": Decimal,
             ...
           }
         }
    → Render reports/tax_summary.html
```

---

## API Design

### Railway GraphQL

- **Endpoint:** `POST https://backboard.railway.com/graphql/v2`
- **Auth:** `Authorization: Bearer {RAILWAY_API_KEY}` — Account Token required (broadest scope)
- **Query:** To be confirmed via GraphiQL introspection during first coding session. Document findings in `docs/api_notes.md`.
- **Error handling:**
  - `401` → raise `RailwayAuthError` (bad/expired token)
  - `429` → raise `RailwayRateLimitError` (implement retry with exponential backoff)
  - `500` / network error → raise `RailwayAPIError` (log and surface to user)
- **Caching:** Do not cache Railway results — always fetch fresh on sync. Results are committed to the DB which serves as the persistent store.

### RBA Exchange Rate

- **Endpoint:** `GET https://api.exchangeratesapi.com.au/{YYYY-MM-DD}/{currency_code}`
- **Auth:** `Authorization: {RBA_API_KEY}` header
- **Response:** JSON with `rate` field for the specified currency.
- **Fallback:** API automatically returns previous business day's rate if requested date has no data (e.g. weekends).
- **Error handling:**
  - `404` → date out of range or currency not supported
  - `429` → monthly limit hit; surface error to user with note to try tomorrow
  - Network error → raise `RBAClientError`; offer manual rate entry as fallback
- **Caching:** Always check `RBARate` table before calling. Save every successful response to the table.

### Anthropic PDF Extraction

- **SDK:** `anthropic` Python package
- **Model:** `claude-opus-4-7`
- **Method:** Base64-encode PDF bytes, send as `document` content type in the API message.
- **Prompt strategy:** Structured JSON extraction prompt specifying exact fields required. Prompt text documented in `docs/api_notes.md`.
- **Error handling:**
  - API error → surface to user, allow manual entry fallback
  - Parse failure (Claude returns unstructured text) → surface raw output to user, allow manual correction
- **Review gate:** Extracted data is always shown to the user before saving. Never auto-commit PDF extraction results.

---

## Data Persistence

- **Development:** SQLite, file at project root (`taxidermatt.db`). Set via `DATABASE_URL=sqlite:///taxidermatt.db` in `.env`.
- **Production:** PostgreSQL, provisioned as a Railway service. `DATABASE_URL` injected by Railway at deploy time.
- **ORM:** SQLAlchemy handles both transparently. No SQL written directly — all queries via ORM.
- **Migrations:** Flask-Migrate (Alembic). Run `flask db migrate` and `flask db upgrade` for every schema change. Never modify the database schema by hand.
- **PDF storage:** `LargeBinary` column on `Expense` (BLOB in SQLite, BYTEA in PostgreSQL). Appropriate for ~100 invoices/year at typical PDF sizes. Revisit if volume grows significantly.
- **Exchange rate cache:** `RBARate` table. Indexed on `(rate_date, currency_code)` for fast lookups.

---

## Setup Instructions

```bash
# 1. Navigate to the project folder
cd "F:\Pycharm Projects\MattTaxApp"

# 2. Create the virtual environment
python -m venv venv

# 3. Activate it
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy and fill in environment variables
copy .env.example .env
# Edit .env with your actual keys

# 6. Initialise the database
flask db upgrade

# 7. Run the development server
flask run
```

**Required `.env` variables:**

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///taxidermatt.db
ANTHROPIC_API_KEY=your-anthropic-key
RAILWAY_API_KEY=your-railway-account-token
RBA_API_KEY=your-exchangeratesapi-key
```

---

## Key Design Decisions

**App Factory pattern (`create_app()`):** Flask best practice. Allows different configs for dev/prod/test, makes the app testable, and prevents circular imports. All extensions (db, login_manager, migrate) are instantiated in `extensions.py` and attached to the app in `create_app()`.

**Flask Blueprints:** Each functional section (auth, expenses, vendors, years, reports) is a separate Blueprint. Keeps routes focused, makes the codebase navigable as it grows.

**SQLite → PostgreSQL via `DATABASE_URL`:** The same SQLAlchemy models work for both. Switching is a one-variable change. This means local dev has zero infrastructure setup.

**RBARate caching table:** The 300/month free limit requires that we never hit the API for a rate we already have. Caching in the DB (rather than in-memory) means the cache survives app restarts and persists across dev sessions.

**PDF storage in DB (not filesystem):** Simpler for Railway deployment — no volume provisioning needed in v1. If invoice volume grows, migrating to a Railway volume or object storage is a well-defined future step.

**Extraction review gate:** Claude's PDF extraction is shown to the user before saving. This protects against misreads of low-quality PDFs and gives Matt control over every record that enters the system.

**TaxCalculator as pure logic:** The tax calculation class takes lists of objects and returns results — no database calls. This makes it trivially testable and easy to update if ATO rules change.

**`SyncResult` return type:** The sync orchestrator returns a structured result object rather than raising on partial failure. A sync run might create 8 records and skip 2 duplicates — both outcomes need to be communicated. Errors are collected and surfaced together after the run completes.

---

## Open Technical Questions

1. **Railway billing query name:** Must be confirmed via GraphiQL introspection with a live Railway API key. First coding task. Document the confirmed query + response fields in `docs/api_notes.md`.

2. **Railway invoice data vs PDFs:** The API almost certainly returns usage metrics and invoice totals, not downloadable PDFs. PDFs must be downloaded manually from the Railway dashboard and uploaded. Confirm during introspection.

3. **RBA weekend/holiday handling:** Confirmed that exchangeratesapi.com.au returns previous business day's rate with a staleness flag. Verify the exact response field name that indicates fallback during coding.

4. **PDF extraction prompt design:** The quality of Claude's extraction depends heavily on the prompt. Treat the extraction prompt as a first-class artifact — iterate and test it against real Railway and Netlify invoices before considering it production-ready.

5. **GST reverse charge on imported services:** When GST-registered, imported services from non-registered overseas suppliers may technically require a reverse charge self-assessment. This is complex and enforcement is low for small businesses. Flag in the BAS report output but do not attempt to automate the calculation in v1.
