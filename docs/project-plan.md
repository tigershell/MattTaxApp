# Project Plan — Taxidermatt

*Created: 25 May 2026*
*Architecture doc: `docs/architecture.md`*

---

## Overview

Taxidermatt is a personal Flask web app for tracking Australian sole trader business expenses and generating ATO tax return output. The build follows the architecture doc: 4 SQLAlchemy models, 3 API clients (Railway, RBA, Anthropic), 5 logic classes, and 6 Flask blueprints.

The existing scaffold (from the initial commit) gives us a head start — `create_app()` is wired, some models exist, and the venv is set up. M0 is about aligning that scaffold with the architecture before building on top of it.

**Test data available:** Three real invoice PDFs are in the project root (`Invoice-EAFZQK-00002.pdf`, `Invoice-EFZYRDMS-0001.pdf`, `namecheap-order-200777863.pdf`). These will be used to test PDF extraction in M2.

---

## Milestones

### Milestone 0: Foundation
**Goal:** Existing scaffold aligned with architecture. All packages installed. App runs, login page loads, Flask-Migrate initialised.

| # | Task | Why | Outputs | Size |
|---|------|-----|---------|------|
| 0.1 | Install `flask-migrate` and `requests`; run `pip freeze > requirements.txt` | Missing from current requirements | `requirements.txt` updated | S |
| 0.2 | Create `src/config.py` with `DevelopmentConfig` and `ProductionConfig` classes | Inline config in `create_app()` needs to move to a config class | `src/config.py` | S |
| 0.3 | Update `src/extensions.py` — add `migrate = Migrate()` alongside existing `db` and `login_manager` | Flask-Migrate needs a `Migrate` instance | `src/extensions.py` updated | S |
| 0.4 | Update `src/__init__.py` — use config class, init `migrate`, register all 6 blueprints (auth, dashboard, expenses, vendors, years, reports) | Current factory registers wrong blueprints and lacks Migrate | `src/__init__.py` updated | S |
| 0.5 | Restructure `src/services/` into `src/api_clients/` and `src/logic/` — create folders and move/rename stub files | Architecture splits services into two clear layers | New folders with `__init__.py` files | S |
| 0.6 | Create stub blueprints for missing routes: `dashboard.py`, `vendors.py`, `years.py` | create_app() will fail to import them without stubs | Stub route files with empty blueprint registered | S |
| 0.7 | Run `flask db init` → `flask db migrate` → `flask db upgrade` | Creates the migrations folder and initial schema | `migrations/` folder, `dev.db` created | S |
| 0.8 | Smoke test: `flask run` → app loads, login page visible, no import errors | Confirms the foundation is solid before building on it | Working dev server | S |
| 0.9 | Commit: `chore: align scaffold with architecture` | Clean checkpoint | Git commit on `dev` | S |

**Estimated total:** ~2–3 hours

---

### Milestone 1: Data Layer
**Goal:** All 4 models fully defined and migrated, vendors pre-seeded, financial year management UI working, login functional.

| # | Task | Why | Outputs | Size |
|---|------|-----|---------|------|
| 1.1 | Rewrite `src/models/expense.py` — add all architecture fields: `vendor_id` (FK), `financial_year_id` (FK), `amount_original`, `currency`, `rba_rate`, `gst_amount`, `invoice_attached`, `source` (enum), `pdf_data` (LargeBinary); add `gst_applies()` and `deductible_amount()` methods | Current Expense model is missing ~60% of its fields | `expense.py` updated | M |
| 1.2 | Create `src/models/financial_year.py` — `FinancialYear` model with `is_gst_registered_on(date)` and `current_year()` classmethod | Core scoping model for all expenses | `financial_year.py` | M |
| 1.3 | Create `src/models/vendor.py` — `Vendor` model with all config fields; no API credentials stored here | Expense records will FK to vendors | `vendor.py` | S |
| 1.4 | Create `src/models/rba_rate.py` — `RBARate` caching model with unique constraint on `(rate_date, currency_code)` | Exchange rate cache to protect 300/month API limit | `rba_rate.py` | S |
| 1.5 | Update `src/models/__init__.py` to import and export all 4 models | Ensures Flask-Migrate discovers all models | `models/__init__.py` | S |
| 1.6 | Run `flask db migrate -m "complete data model"` → `flask db upgrade` | Applies the full schema to the dev DB | New migration file, `dev.db` updated | S |
| 1.7 | Create `src/logic/seeder.py` — a `DatabaseSeeder` class with a `seed_vendors()` method that creates the 6 pre-configured vendors (Anthropic, Railway, OpenAI, Fal.ai, Netlify, Namecheap) with correct defaults | Vendors need to exist before any expenses can be created | `seeder.py` | S |
| 1.8 | Add `flask seed` CLI command to `src/__init__.py` using `@app.cli.command()` | One-command vendor setup on any fresh install | CLI command in `__init__.py` | S |
| 1.9 | Confirm `src/models/user.py` has correct password hashing (Werkzeug `generate_password_hash`/`check_password_hash`) and Flask-Login integration | Login must work before any protected routes are useful | `user.py` verified/updated | S |
| 1.10 | Add `flask create-admin` CLI command — prompts for username/password, creates the single admin user | No way to log in without a user in the DB | CLI command | S |
| 1.11 | Build `years` blueprint — list all financial years, form to set GST registration date | Financial year is the top-level scope for all data | `routes/years.py`, `templates/years/list.html` | M |
| 1.12 | Build `vendors` blueprint — list all vendors, edit vendor config form | Vendors are the reference data the whole app depends on | `routes/vendors.py`, `templates/vendors/list.html`, `templates/vendors/edit.html` | M |
| 1.13 | Build `dashboard` blueprint — show current FY, expense count, total AUD spend, link to sync/upload | First thing Matt sees after login; confirms the app is alive | `routes/dashboard.py`, `templates/dashboard/index.html` | M |
| 1.14 | Apply design system CSS to `base.html` and all M1 templates — phosphor green on near-black, IBM Plex Mono | Branding is already designed; apply it now so every template looks right from the start | `static/css/style.css`, `base.html` updated | M |
| 1.15 | Commit: `feat: complete data layer — models, migrations, vendor seed, year and vendor UI` | Milestone checkpoint | Git commit + tag `v0.1.0-m1` | S |

**Estimated total:** ~8–12 hours
**Dependency:** M0 complete.

---

### Milestone 2: PDF Upload + Expense Capture
**Goal:** Drop a PDF → Claude extracts structured data → user reviews and confirms → expense saved to DB. Core workflow end-to-end.

| # | Task | Why | Outputs | Size |
|---|------|-----|---------|------|
| 2.1 | Register for exchangeratesapi.com.au free API key; add `RBA_API_KEY` to `.env` and `.env.example` | Needed before any USD expense can be saved | API key obtained | S |
| 2.2 | Write `src/api_clients/rba_client.py` — `RBAClient` class: `get_rate(date, currency)` → checks `RBARate` cache first, fetches from API on miss, saves to cache | Every USD expense needs a rate; caching protects the free tier | `rba_client.py` | M |
| 2.3 | Write `src/logic/currency_converter.py` — `CurrencyConverter` class: `convert(amount, currency, date)` → returns `(aud_amount, rate_used)`; `manual_override(amount, rate)` for fallback | USD→AUD conversion is needed at PDF save time | `currency_converter.py` | S |
| 2.4 | Write tests for `CurrencyConverter` — test with a known RBA rate for a real historical date | Currency conversion is a calculation that must be correct | `tests/test_currency_converter.py` | S |
| 2.5 | Design the PDF extraction prompt for `PDFExtractor` — test it against the three real invoice PDFs in the project root before writing any code | The prompt is the most important part; get it right before wiring it up | Prompt text documented in `docs/api_notes.md` | M |
| 2.6 | Write `src/api_clients/pdf_extractor.py` — `PDFExtractor` class: `extract(pdf_bytes)` → base64 encode → send to `claude-opus-4-7` → parse response → return dict | Core AI extraction class | `pdf_extractor.py` | M |
| 2.7 | Write `src/logic/duplicate_detector.py` — `DuplicateDetector` class: `find_match(vendor_id, date, amount)` → query Expense table with ±1 day / ±$0.01 tolerance | Prevents duplicate records when PDF is uploaded after an API sync | `duplicate_detector.py` | S |
| 2.8 | Write tests for `DuplicateDetector` — test exact match, near match (within tolerance), and no match cases | Logic must be correct or expenses will be duplicated or missed | `tests/test_duplicate_detector.py` | S |
| 2.9 | Build the upload route — `POST /upload` receives PDF file, calls `PDFExtractor.extract()`, renders confirmation page with extracted data pre-filled in an editable form | User must review before saving; never auto-commit extraction results | `routes/expenses.py` or `routes/upload.py`, `templates/upload/index.html` updated | M |
| 2.10 | Build the upload confirm route — `POST /upload/confirm` receives the confirmed form data, calls `DuplicateDetector`, calls `CurrencyConverter` if needed, saves `Expense` | Commits the expense to DB after user review | Confirm route + `templates/upload/confirm.html` | M |
| 2.11 | Handle extraction errors gracefully — if Claude returns unparseable output, show the raw text alongside an empty editable form so Matt can enter the data manually | Low-quality PDFs or unusual layouts will occasionally fail | Error state in upload template | S |
| 2.12 | Test end-to-end with each of the three real invoice PDFs in the project root | Real invoices are the only meaningful test | Manual test, note results in `docs/api_notes.md` | S |
| 2.13 | Commit: `feat: PDF upload and expense capture — Claude extraction, currency conversion, duplicate detection` | Milestone checkpoint | Git commit + tag `v0.1.0-m2` | S |

**Estimated total:** ~8–12 hours
**Dependency:** M1 complete. RBA API key obtained (2.1).

---

### Milestone 3: Railway API Sync
**Goal:** "Sync Railway" button fetches billing data from Railway's GraphQL API and creates expense records automatically.

| # | Task | Why | Outputs | Size |
|---|------|-----|---------|------|
| 3.1 | Get a Railway Account Token from the Railway dashboard (Settings → Tokens); add `RAILWAY_API_KEY` to `.env` and `.env.example` | Account Token has billing scope; Project Token does not | API key obtained | S |
| 3.2 | Open `railway.com/graphiql` with the Account Token; explore the schema to find the billing/invoice query; document the exact query, variables, and response fields in `docs/api_notes.md` | Billing queries are not in Railway's public docs — must be discovered via introspection | `docs/api_notes.md` updated with confirmed query | M |
| 3.3 | Write `src/api_clients/railway_client.py` — `RailwayClient` class: `get_billing_history(from_date, to_date)` using the confirmed query; `_handle_error()` for 401/429/500 | Railway API sync is the automated capture core | `railway_client.py` | M |
| 3.4 | Write `src/logic/sync_orchestrator.py` — `SyncOrchestrator` class: `run_railway_sync(financial_year)` → calls client → calls `DuplicateDetector` → calls `CurrencyConverter` → creates Expense records → returns `SyncResult` | Coordinates the full sync workflow | `sync_orchestrator.py` | M |
| 3.5 | Write tests for `SyncOrchestrator` — mock `RailwayClient` to return fixture data; verify correct Expense records are created and duplicates skipped | Tests should not hit the real Railway API | `tests/test_sync_orchestrator.py` | M |
| 3.6 | Add sync route `POST /expenses/sync-railway` to expenses blueprint; call `SyncOrchestrator`; flash result message (N created, M skipped) | Gives Matt a button to trigger sync | `routes/expenses.py` updated | S |
| 3.7 | Add "Sync Railway" button to dashboard; show last sync result | Entry point for the sync workflow | `templates/dashboard/index.html` updated | S |
| 3.8 | Add `POST /expenses/<id>/attach-pdf` route — attaches a PDF to an existing expense record created by API sync; sets `invoice_attached=True` | API sync creates records without PDFs; this is how Matt attaches them later | Route in `routes/expenses.py`, button on expense detail page | S |
| 3.9 | Test sync with real Railway account — verify records created match actual billing history | Real API test | Manual test, results noted | S |
| 3.10 | Commit: `feat: Railway API sync — auto-create expense records from billing history` | Milestone checkpoint | Git commit + tag `v0.1.0-m3` | S |

**Estimated total:** ~6–10 hours
**Dependency:** M2 complete. Railway Account Token obtained (3.1). Schema discovered (3.2) before 3.3 can start.
**Risk:** Schema discovery (3.2) is the wild card — Railway's billing query is undocumented. Budget extra time here.

---

### Milestone 4: Reporting
**Goal:** ATO tax summary report and BAS report (dormant until GST registered) both working with real data.

| # | Task | Why | Outputs | Size |
|---|------|-----|---------|------|
| 4.1 | Write `src/logic/tax_calculator.py` — `TaxCalculator` class: `apply_gst_rules(expenses, gst_date)`, `group_by_ato_category(expenses)`, `total_deductible(expenses)`, `total_gst_credits(expenses)` | Core tax logic; no DB calls, pure calculation on lists | `tax_calculator.py` | M |
| 4.2 | Write thorough tests for `TaxCalculator` — test pre-GST expenses (full amount deductible), post-GST expenses (split GST as ITC), mixed FY, and zero-expense edge cases | Tax calculations must be correct; this is the most critical test file in the project | `tests/test_tax_calculator.py` | M |
| 4.3 | Write `src/logic/report_generator.py` — `ReportGenerator` class: `tax_summary(financial_year)` returns structured dict with categories, totals, and myTax field mapping; `bas_report(financial_year, quarter)` returns GST summary | Produces the data the report templates will render | `report_generator.py` | M |
| 4.4 | Build reports blueprint — `GET /reports/tax-summary?year_id=X` and `GET /reports/bas?year_id=X&quarter=N` routes | Entry points for the two reports | `routes/reports.py` | S |
| 4.5 | Build `tax_summary.html` — table of expenses grouped by ATO category with subtotals; myTax field mapping section at the bottom showing "D15 Other deductions: $X.XX" etc. | The primary output of the whole app | `templates/reports/tax_summary.html` | M |
| 4.6 | Build `bas.html` — shows "BAS reporting not yet active — enter your GST registration date in Financial Years to activate" when no GST date set; shows quarterly GST summary when active | Designed now, activates automatically when GST date entered | `templates/reports/bas.html` | M |
| 4.7 | Test reports with real expense data entered in M2/M3 — verify totals match what is expected | Reports must be correct before they can be trusted | Manual test | S |
| 4.8 | Commit: `feat: ATO tax summary and BAS reports` | Milestone checkpoint | Git commit + tag `v0.1.0-m4` | S |

**Estimated total:** ~6–10 hours
**Dependency:** M3 complete (real expense data needed to test reports meaningfully).

---

### Milestone 5: Polish & Deploy Prep
**Goal:** GST rules applied correctly, UX complete, test suite green, app ready to hand to the Deploy skill.

| # | Task | Why | Outputs | Size |
|---|------|-----|---------|------|
| 5.1 | Implement and test GST registration date flow — entering the date in the years UI should immediately change how `TaxCalculator` treats subsequent expenses; test with a split-FY scenario | Matt plans to register before 30 June 2026; this must work correctly | `years` route update, TaxCalculator integration test | M |
| 5.2 | Add manual expense entry route and form — `GET/POST /expenses/new` for expenses not covered by API sync or PDF upload (e.g. cash receipts) | Edge case but needed for completeness | `routes/expenses.py`, `templates/expenses/edit.html` | M |
| 5.3 | Flash messages and user-facing error handling across all routes — sync errors, API failures, extraction failures, form validation | Errors should surface clearly, not silently fail | All route files updated | M |
| 5.4 | Expense list and detail pages — list all expenses for current FY with filter by vendor/category; detail page shows all fields, attachment status, and attach PDF button | Matt needs to review and manage his expense records | `templates/expenses/list.html`, `templates/expenses/detail.html` | M |
| 5.5 | Complete the test suite — ensure all logic classes have meaningful tests; run `pytest` and fix any failures | A green test suite is the deploy gate | All test files complete, `pytest` passes | M |
| 5.6 | Final CSS pass — ensure design system is consistently applied across all templates; check all pages in browser | The branding brief is fully designed; the app should look like it | All templates reviewed | M |
| 5.7 | Update `README.md` with accurate setup instructions — venv creation, env vars, `flask db upgrade`, `flask seed`, `flask create-admin`, `flask run` | Any new machine (or Railway) needs to be able to run this from the README | `README.md` | S |
| 5.8 | Confirm `.env.example` lists every required variable with a comment | Makes it clear what needs to be filled in | `.env.example` | S |
| 5.9 | Move the three test invoice PDFs out of the project root into a `tests/fixtures/` folder; add to `.gitignore` if they contain real financial data | Project root should be clean; PDFs shouldn't be committed | `tests/fixtures/` | S |
| 5.10 | Final smoke test of every route — log in, sync Railway, upload a PDF, view reports, set GST date, view BAS | End-to-end confidence before deploy | Manual test checklist | S |
| 5.11 | Commit and tag: `feat: polish, GST rules, full test suite — MVP complete` + `git tag -a v0.1.0 -m "MVP complete"` | Release checkpoint | Git commit + tag `v0.1.0` on `dev`, merge to `main` | S |

**Estimated total:** ~8–12 hours
**Dependency:** M4 complete.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Railway billing query not discoverable via GraphiQL | Low | High | Railway's dashboard uses the same API — the data is there. Allow extra time for schema exploration (3.2). |
| Railway API returns usage metrics, not invoice totals | Medium | Medium | Design SyncOrchestrator to handle whatever shape the billing data takes. PDFs are the fallback for ATO substantiation regardless. |
| Claude PDF extraction fails on some invoice layouts | Medium | Low | Extraction always goes through a user confirmation step — Matt can correct the fields manually. Iterate the prompt against real invoices (2.5). |
| RBA rate not available for a specific date (weekend/holiday) | High (frequent) | Low | exchangeratesapi.com.au falls back automatically to previous business day. Handle the staleness flag in RBAClient. |
| Flask-Migrate conflicts when rewriting Expense model | Medium | Medium | Delete `dev.db` and run `flask db upgrade` fresh in dev. Migrations are only a production concern once the app is deployed. |
| GST registration date not confirmed before 30 June 2026 | Medium | Medium | App is designed to handle both states. The BAS report activates automatically when the date is entered — no rebuild needed. |

---

## Definition of Done

A task is complete when:
- Code is written and manually tested in the browser or via `pytest`
- The feature works as described in the architecture doc
- No obvious errors or crashes under normal use
- Committed to `dev` with a clear commit message (e.g. `feat: ...`, `fix: ...`, `test: ...`)
- `requirements.txt` updated if a new package was installed

A milestone is complete when:
- All tasks in that milestone are done
- The app runs cleanly from a fresh `flask run`
- Committed and tagged in Git

---

## Setup Commands (for reference during coding)

```bash
# Activate venv
venv\Scripts\activate

# Install a new package
pip install package-name
pip freeze > requirements.txt

# Database migrations
flask db migrate -m "description of change"
flask db upgrade

# Seed vendors
flask seed

# Create admin user
flask create-admin

# Run tests
pytest

# Run dev server
flask run
```

---

## Git Tagging at Milestones

```bash
git tag -a v0.1.0-m1 -m "Milestone 1: Data layer complete"
git push origin --tags
```

Tag every milestone. It creates a clean history and makes it easy to roll back if something breaks.