# Logic Notes — Taxidermatt

*Updated: 25 June 2026*

This file documents non-obvious decisions, data flows, and implementation quirks. Update it when anything surprising is discovered during coding.

---

## Exchange Rate API

**Provider changed: exchangeratesapi.com.au → Frankfurter**

The original planned provider (exchangeratesapi.com.au) was found to require a paid plan ($29/month) for all historical rate lookups, including today's date. The free tier provides no usable data.

Switched to **Frankfurter** (`api.frankfurter.app`):
- Completely free, no API key required
- ECB (European Central Bank) sourced daily rates
- Historical data back to 1999
- Returns AUD per 1 unit of foreign currency directly — no inversion needed
- Weekends/holidays automatically fall back to the prior business day

The `RBA_API_KEY` env var is now unused but left in `.env.example` for reference. The `RBARate` DB table and `RBAClient` caching logic are unchanged — the cache still protects against redundant API calls.

**Rate direction:** Frankfurter returns `{"rates": {"AUD": 1.608}}` when queried `?from=USD&to=AUD`. This means 1 USD = 1.608 AUD. This is the correct direction for `amount_aud = amount_original * rate`. No inversion is applied (unlike the old client which inverted).

---

## Vendor Matching

`_match_vendor()` in `routes/upload.py` tries to match an extracted vendor name string against the `vendors` table.

**Two-pass approach:**
1. Substring check — does the DB vendor name appear in the extracted string, or vice versa?
2. Token overlap — split both strings on non-alphanumeric chars, filter tokens < 3 chars, check if any token from the DB name appears in the extracted tokens

**Why token overlap was needed:** Fal.ai's invoice says `"fal - Features & Labels, Inc."`. Substring check fails (neither contains the other). Token check finds `"fal"` in both → match.

The minimum token length of 3 avoids false positives from short common words ("of", "in", etc.) while still catching meaningful short names.

---

## PDF Upload — Temp File Queue

PDFs are stored in OS temp files between the upload step and confirm step because:
- Flask session size is limited (cookie-based); a 500KB PDF would overflow it
- Storing the path in the session is safe for a single-user local app

**Multi-file queue:** When multiple PDFs are dropped, all are written to temp files immediately. The first file is shown on the confirm form. The rest are stored as a list of `{path, filename}` dicts in `session["upload_queue"]`. After each confirm, the next item is popped from the queue and shown.

**Cleanup:** Temp files are deleted (`os.unlink`) when the confirm route reads them. If the user abandons the flow mid-queue, orphaned temp files remain in the OS temp directory until the OS cleans them. This is acceptable for a personal app — the OS temp dir is regularly cleaned.

---

## Duplicate Detection

`DuplicateDetector.find_match()` uses:
- Exact `vendor_id` match
- Invoice date within ±1 day (handles timezone/settlement date ambiguity)
- `amount_aud` within ±$0.01 (handles rounding differences)

**Duplicate handling on re-upload:**
- Duplicate found + existing record **already has a PDF** → skipped with an informational flash. No changes made.
- Duplicate found + existing record **has no PDF** → PDF is attached to the existing record. This handles the workflow where Railway sync creates a record first and the PDF is uploaded later.

**Duplicates must not halt a bulk upload.** Originally a duplicate did `redirect(...)` to the existing expense, which silently abandoned the rest of `session["upload_queue"]` — so one duplicate killed the whole batch. Both the save path and the duplicate path now call the shared `_advance_queue()` helper, which moves to the next queued file (or falls back to a final redirect when the queue is empty). This keeps bulk re-uploads moving past invoices that are already saved. (Note: a currency-conversion failure on a USD invoice still ends the batch via an error redirect — a candidate for the same skip-and-continue treatment if it becomes a problem.)

---

## New Vendor Creation from Upload

When a PDF is uploaded for an unknown vendor, the confirm form shows `"— Add new vendor —"` pre-selected in the vendor dropdown (when no match is found). Inline fields appear for name, currency, ATO category, and GST flag.

On confirm submission:
1. A `Vendor` is created and `db.session.flush()` called to get its ID without committing
2. The `Expense` is then created referencing `vendor.id`
3. Both are committed together in a single transaction

`flush()` vs `commit()` is used so the whole operation (vendor + expense) either succeeds or rolls back together if an error occurs before the commit.

---

## Session Data Keys

| Key | Set in | Cleared in | Content |
|-----|--------|------------|---------|
| `pending_pdf_path` | `upload()` | `confirm()` | Path to current temp PDF file |
| `pending_filename` | `upload()` | `confirm()` | Original filename for display |
| `upload_queue` | `upload()` | `confirm()` (pops items) | List of `{path, filename}` for remaining files |

---

## Search Filtering (Client-Side)

Both the expenses list and vendor detail page use client-side JS filtering. Each table row has a `data-search` attribute containing a lowercase concatenation of all searchable fields. The input listener checks `row.dataset.search.includes(term)` on every keystroke.

This approach is appropriate for a personal app where the total number of rows is in the hundreds, not tens of thousands. No backend round-trip, no debouncing needed.

Searchable fields per page:
- **Expenses list:** vendor name, invoice number, ATO category, description
- **Vendor detail:** date, invoice number, AUD amount, description

---

## Financial Year Scoping

All expenses belong to a `FinancialYear` (1 Jul – 30 Jun). Records are filed under the year containing **their own date** — invoice date for expenses/uploads, received date for income — via `FinancialYear.get_or_create_for_date()`, never today's date. Editing a record's date re-files it under the matching year. List views and the dashboard default to the current year via `get_or_create_current()`.

Financial years are read-only records — label and dates only. Each card on the Financial Years page links to `/report?year=<id>`, which is how past years' tax summaries are viewed.

---

## GST Registration — an app-wide setting, not a per-year one

`BusinessSettings` (`models/business_settings.py`) is a single-row table holding `gst_registration_date`. It is the dividing line, and the **same logic governs both expenses and income**:
- Expenses before this date: full `amount_aud` is deductible. On or after: `amount_aud - gst_amount` is deductible (GST becomes an Input Tax Credit).
- Income before this date: full amount is assessable, no GST. On or after: GST collected is owed to the ATO (output tax) and the ex-GST amount is assessable.

The date is null until Matt registers for GST. The BAS / GST position in the tax report activates automatically when it is entered.

### Why it moved off `FinancialYear` (fixed 2026-07-09)

`gst_registration_date` originally lived on `FinancialYear`. This was wrong: you register for GST **once**, and stay registered until you cancel — it does not restart each July. The consequences were real and silent:

- Every new financial year started with a null date, so `gst_applies()` returned `False` for all of its records. That year's expenses claimed **no Input Tax Credits** and were deducted GST-inclusive (overstating deductions, understating the BAS refund).
- The date input was clamped with `min`/`max` to the year's own range, so a registration date from a *prior* year could not even be entered into a later year. The data model made the correct answer unrepresentable.

This surfaced on the rollover into FY 2026-27, which appeared as "Not GST registered" with one expense already recorded against it.

A single registration date is interpreted per-year by two `FinancialYear` helpers, so the year-level view is derived rather than stored:
- `gst_applies_during(reg_date)` → was the business registered at any point in this year? (False for years that ended before registration — those have no BAS position at all.)
- `gst_status(reg_date)` → `"Not GST registered"` / `"GST registered from <date>"` / `"GST registered (whole year)"`

**Known limitation:** a single date cannot express GST *de-registration* (registering, cancelling, then re-registering). If that ever happens, this needs to become a date range or a list of registration periods.

### `BusinessSettings.get()` never writes

`get()` returns an unsaved default when no row exists, and memoises the row on Flask's `g` for the request. It deliberately does **not** insert or commit, because `gst_applies()` is called from inside request handlers that may have their own uncommitted changes pending — a commit there would flush a half-built expense to disk. Use `get_or_create()` (which commits) only when actually saving a setting.

---

## Income Tracking

`models/income.py` is the income-side mirror of `Expense`. Each `Income` row stores the gross AUD amount received and an optional `gst_amount` (GST collected). GST treatment reuses the business-wide registration date via the same helpers as expenses:

- `gst_applies()` → `BusinessSettings.get().is_gst_registered_on(received_date)`
- `gst_payable()` → GST collected that is owed to the ATO (output tax), or `0.00` when GST doesn't apply
- `assessable_amount()` → `amount_aud - gst_payable()` (the income-tax-assessable, ex-GST portion)

**Why this matters:** income received on a setup that pre-dates GST registration carries no GST automatically — the full amount is assessable and nothing is owed. Income on/after registration is treated as GST-inclusive (GST = 1/11th of the gross).

Entry is **manual** for now (`routes/income.py`, mirroring the expense routes' inline form parsing). Stripe API sync is a future milestone. **Stripe fees** are recorded as a separate `Expense` (so the fee, and any GST on it, is captured as a deduction) rather than netted off income — income is recorded gross.

---

## Tax Report — Income vs Expenses

`services/tax_report_service.py` produces three views for the current financial year:

1. **Income tax** — total assessable income (ex-GST) minus total deductible expenses (ex-GST) = net profit or loss. Expenses are summed with `deductible_amount()`, **not** raw `amount_aud` (the previous version summed the raw amount, which over-stated deductions once GST-registered — fixed).
2. **GST / BAS** — GST collected on sales (output tax) minus GST paid on purchases (Input Tax Credits) = net owed to / refundable from the ATO.
3. **myTax instructions** — built dynamically from the real figures (income is no longer hard-coded to $0.00) and switches between the profit and loss wording.

The dashboard shows the same income/spend/net headline figures.

---

## Backups

`logic/backup_manager.py` (`BackupManager`) creates and restores SQLite snapshots using SQLite's **online backup API** (`sqlite3.Connection.backup`), so a snapshot is consistent even while the dev server is running. The live DB path is read from the resolved engine URL (`db.engine.url.database`), not the raw config string, so it's correct regardless of how Flask-SQLAlchemy resolved a relative URI.

- **In-app:** a **Backup** page (`routes/backup.py`) with a one-click "Download backup now" (creates a snapshot in `backups/` *and* streams it to the browser), a list of existing backups, and **Restore** (which snapshots the current DB first, so a restore can never lose present data).
- **CLI:** `flask backup` and `flask restore <file>` do the same for dev/ops use (e.g. before running a migration).
- `backups/` is gitignored — snapshots contain real financial data and invoice PDFs.

Only SQLite is supported; a hosted Postgres DB would use the provider's managed backups instead.

---

## Test Isolation (data-loss fix)

`create_app()` accepts a `config_overrides` dict applied **after** `from_object` but **before** `db.init_app()`. This exists because Flask-SQLAlchemy 3.x binds its engine inside `init_app()` — so setting `app.config["SQLALCHEMY_DATABASE_URI"]` *after* `create_app()` (as the old `conftest.py` did) was silently ignored, and the test suite's `create_all()`/`drop_all()` ran against the **real dev database**, dropping live data.

`tests/conftest.py` now passes the in-memory URI through `create_app({...})`, guaranteeing the engine binds to `sqlite:///:memory:` before any table operation. Verified: the test engine resolves to `:memory:` and the suite cannot touch the real DB.

---

## Known Limitations / Future Work

- **Revenue tracking:** manual income entry is now in (`Income` model + entry pages, wired into the tax report). Automated revenue sync — Stripe, App Store Connect, Google Play — is still not wired in. Design decision: wait until revenue is actually flowing before connecting these APIs, so the integration matches the real data format.
- **Bulk upload still confirms one invoice at a time:** by design (review each extraction), but duplicates no longer halt the batch. A USD invoice whose exchange-rate lookup fails will still stop the batch.
- **Railway API sync:** Billing queries are undocumented — schema discovery via GraphiQL is required before this can be built (M3).
- **PDF temp file cleanup:** Abandoned mid-queue uploads leave orphaned temp files. Acceptable for now; could add a cleanup task later.
- **Exchange rates:** Frankfurter uses ECB data, not literally RBA rates. For ATO purposes this is acceptable for small business expenses. If exact RBA rates are ever required, the `RBAClient` can be updated to use a different source without changing `CurrencyConverter`.
