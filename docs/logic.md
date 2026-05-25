# Logic Notes — Taxidermatt

*Updated: 25 May 2026*

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
- Duplicate found + existing record **already has a PDF** → blocked with error flash, redirect to existing expense. No changes made.
- Duplicate found + existing record **has no PDF** → PDF is attached to the existing record. This handles the workflow where Railway sync creates a record first and the PDF is uploaded later.

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

All expenses belong to a `FinancialYear` (1 Jul – 30 Jun). The current year is created automatically on first access via `FinancialYear.get_or_create_current()`.

The `gst_registration_date` field on `FinancialYear` is the dividing line:
- Expenses before this date: full `amount_aud` is deductible
- Expenses on or after: `amount_aud - gst_amount` is deductible (GST becomes an Input Tax Credit)

This field is null until Matt registers for GST. The BAS report activates automatically when the date is entered.

---

## Known Limitations / Future Work

- **Revenue tracking:** Stripe, App Store Connect, and Google Play revenue are not yet wired in. Design decision: wait until revenue is actually flowing before connecting these APIs, so the integration matches the real data format.
- **Railway API sync:** Billing queries are undocumented — schema discovery via GraphiQL is required before this can be built (M3).
- **PDF temp file cleanup:** Abandoned mid-queue uploads leave orphaned temp files. Acceptable for now; could add a cleanup task later.
- **Exchange rates:** Frankfurter uses ECB data, not literally RBA rates. For ATO purposes this is acceptable for small business expenses. If exact RBA rates are ever required, the `RBAClient` can be updated to use a different source without changing `CurrencyConverter`.
