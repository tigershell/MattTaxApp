# Product Design Brief — Taxidermatt

## One-Line Summary
A personal, locally-deployed web app for an Australian sole trader developer to automatically capture, store, and report business expenses for the ATO tax return — with API integrations into the developer services he actually uses.

---

## Problem Statement
An Australian sole trader who is also a full-time employee spends money throughout the year on developer services (hosting, AI APIs, domains, trademark filings) that are legitimate tax deductions. Today there is no tool that:
- Automatically captures billing data from developer-specific services (Railway, Netlify, Anthropic, OpenAI, Fal.ai, Namecheap)
- Handles the AUD/USD currency conversion using ATO-acceptable RBA exchange rates
- Correctly handles the transition from non-GST to GST-registered status
- Produces ATO myTax field-by-field instructions at the end of the financial year

The result is manual tracking, missed deductions, and tax-time scrambling.

---

## Target User
Matt — Adelaide-based developer. Full-time employed + sole trader software development business (no GST registration currently, planning to register before 30 June 2026). Not earning business income yet; accumulating deductible expenses. Plans to publish apps to App Store and Google Play. Manages expenses across 6+ developer service platforms, most billed in USD.

This is a personal tool. Commercial release is not planned for v1 but the architecture should not prevent it.

---

## User Journey
1. App auto-syncs with connected vendor APIs (Railway first; others as integrations are built) and creates expense records flagged "invoice not yet attached"
2. Matt drops PDF invoices into the upload window (for Netlify, Namecheap, and any vendor without an API)
3. Claude API extracts the structured data from the PDF
4. If the expense already exists from an API sync, the PDF is matched and attached — no duplicate created
5. For USD expenses, the app auto-fetches the RBA exchange rate for the invoice date and stores both the original and AUD amounts
6. At tax time, Matt opens the report, sees a breakdown by ATO category with all AUD totals, and gets field-by-field myTax instructions
7. When GST registration happens, Matt enters the effective date — the app adjusts all subsequent records to split GST as Input Tax Credits and unlocks BAS reporting

---

## Value Proposition
The only expense tracker built specifically for a developer's toolchain. Every service Matt pays for is either auto-imported or extracted from a PDF by AI — nothing falls through the cracks, currency conversion is handled correctly, and the output is tailored precisely to his ATO tax situation including non-commercial loss rules and the pre/post-GST transition.

---

## Competitive Landscape

**Searches performed:**
- "Australian sole trader expense tracking app tax return 2026"
- "Best expense tracking software Australian freelancer sole trader ATO"
- "TaxTank sole trader Australia features automatic expense import"
- "Hnry Australia sole trader features pricing review 2026"
- "Expense tracking app automatic import Railway Netlify Anthropic OpenAI billing developer"

**Top competitors identified:**
- **TaxTank (Sole Tank)** — $6/month, Australian-made, Open Banking bank feeds (180+ banks), non-commercial loss calculations, BAS reporting. Most direct competitor for the tax logic.
- **Hnry** — 1% of income capped $1,500/yr, full automated tax service including lodgement. Designed for people earning through the platform; overkill for $0 income.
- **ATO myDeductions** — free, built into the ATO app, basic manual tracking only.
- **Xero / MYOB / Rounded / FreshBooks** — general accounting software, no developer toolchain integrations.

**Closest match and how it overlaps:**
TaxTank covers the Australian tax logic well (non-commercial losses, BAS, ATO categories) and auto-imports via bank feeds. However, bank feeds capture the *transaction*, not the *tax invoice PDF*. ATO substantiation requires the actual invoice. None of the competitors auto-connect to Railway, Netlify, Anthropic, OpenAI, Fal.ai, or Namecheap.

**Real, user-noticeable differentiator:**
Direct API integration with the exact developer services Matt uses — creating expense records automatically with the correct ATO categories, storing PDFs, handling USD→AUD conversion via RBA rates, and producing myTax-ready output. No existing tool does this.

**Decision:** Cleared to proceed as a personal tool. The market is served for general sole traders but not for a developer's specific toolchain.

---

## Name & Brand Status

- **Working name:** Taxidermatt
- **Naming rationale:** Portmanteau of "tax" + "taxidermy" (preserving records) + "Matt". Tagline: *"Preserving your finances, one invoice at a time."*
- **Trademark check (IP Australia):** Not formally run — user decision. Name is a unique portmanteau of the user's own name with no existing web, app store, or social media presence.
- **Trademark check (USPTO):** Not formally run — same decision.
- **Domain status:** taxidermatt.com — not resolving (appears unregistered). taxidermatt.com.au — not resolving (appears unregistered). Both available to register.
- **App store check:** No iOS or Android app found with this name.
- **Social handle availability:** No accounts found on any platform.
- **Decision:** Cleared to proceed. Personal tool; trademark risk accepted by user.

---

## API & Commercial Dependency Audit

**Critical APIs identified:**

| Service | Role | Critical? | Currency | Charges GST? |
|---------|------|-----------|----------|--------------|
| Anthropic SDK | PDF extraction via Claude | Critical | AUD | Yes |
| Railway GraphQL API | Auto-import billing data | Critical | USD | No |
| RBA Exchange Rate API | USD→AUD conversion | Critical | N/A | N/A |
| Anthropic Usage & Cost API | Auto-import spend data | Enhancement | USD | — |
| OpenAI Usage API | Auto-import spend data | Enhancement | USD | No |
| Fal.ai Platform API | Auto-import balance/billing | Enhancement | USD | No |
| Netlify | PDF upload only (no billing API) | N/A | USD | No |
| Namecheap | PDF upload only (no billing API) | N/A | USD | No |

**API findings:**

- **Anthropic SDK** — open commercial access, standard API pricing. Used only at upload time for PDF extraction. ✅
- **Railway GraphQL API** — public API at `backboard.railway.com/graphql/v2`, includes billing and usage queries, actively maintained. ✅
- **RBA Exchange Rate** — published daily via RSS and via free REST API (exchangeratesapi.com.au, 300 calls/month free). ATO explicitly accepts RBA rates for foreign currency conversion. ✅
- **Anthropic Usage & Cost API** — `/v1/organizations/cost_report` endpoint, requires admin API key. Returns USD spend data; Anthropic invoices Matt in AUD+GST so the API data and invoice amount will differ. ⚠️ Use for auto-creating records; still need PDF attached for ATO.
- **OpenAI Usage API** — programmatic spend data available, invoices are USD PDF downloaded from dashboard. ⚠️ Same pattern as Anthropic.
- **Fal.ai Platform API** — basic billing/credit balance data available. Detailed FOCUS reports are enterprise-only. ⚠️ Limited auto-import only.
- **Netlify** — no programmatic billing API for non-enterprise. Invoices via UI only. ❌ PDF upload only.
- **Namecheap** — account balance API exists, no invoice retrieval API. ❌ PDF upload only.

**ToS — commercial use permitted:** Yes for all services (personal use, not reselling).
**Platform risk rating:** Low — all services are established platforms with stable developer APIs.
**Fallback:** PDF upload covers all vendors regardless of API status.

**Decision:** Cleared to proceed. All critical APIs confirmed. Enhancement integrations (Anthropic usage, OpenAI, Fal.ai) to be built progressively after Railway.

**AI API cost estimate:**
- PDF extraction: ~3,000 input tokens + 200 output tokens per invoice using claude-opus-4-7
- Cost per extraction: ~$0.05–0.10 AUD
- ~10–20 invoices/month = ~$0.50–$2.00/month
- Trivial for personal use.

---

## MCP Architecture & Ecosystem Check

- **Product architecture type:** Conventional Flask web app calling external APIs directly. Not an MCP server. Not consuming MCPs.
- **MCP ecosystem search:** N/A — this is a standard web app using REST/GraphQL APIs. The Anthropic SDK is used directly, not via MCP.
- **Usage gate approach:** N/A — personal tool, no monetisation.

---

## MVP Feature Set

### Financial Year Management
- Financial years as first-class records (start/end dates, GST registration date)
- Auto-create new year on 1 July
- Browse and view historical years
- All expense records scoped to a financial year

### Vendor Management
- Vendor configuration section with per-vendor settings:
  - API integration available (yes/no)
  - API credentials (stored securely in .env/DB)
  - Invoice PDF required for ATO (yes/no)
  - Default currency (AUD/USD/etc.)
  - Charges GST (yes/no)
  - Default ATO category
  - Sync frequency (monthly/on-demand)
  - Notes
- Pre-seeded with: Anthropic, Railway, OpenAI, Fal.ai, Netlify, Namecheap

### Expense Capture
- **API sync:** Railway GraphQL integration auto-creates expense records (flagged "invoice not yet attached")
- **PDF upload:** Drop in any PDF → Claude API extracts vendor, date, amount, currency, category, description
- **Duplicate detection:** When a PDF is uploaded, match against existing API-sourced records by vendor + date + amount and attach rather than duplicate

### Data Model
Each expense record stores:
- Vendor (linked to vendor table)
- Invoice date
- Amount in original currency
- Original currency code
- RBA exchange rate on invoice date
- Amount in AUD (calculated)
- GST amount (if applicable)
- ATO category
- Description
- Notes
- PDF invoice (stored as binary)
- Invoice attached flag
- Financial year (FK)
- Source (api_sync / pdf_upload / manual)

### Currency Handling
- Auto-fetch RBA exchange rate for the invoice date
- Store original currency amount, rate used, and AUD equivalent
- Manual override if RBA feed unavailable

### GST Management
- GST registration toggle with effective date
- Pre-registration: full AUD amount is deductible, GST component noted but not separated
- Post-registration: GST split out as Input Tax Credit, ex-GST amount is the deductible expense
- BAS report: shows GST collected (income) vs GST paid on inputs (ITC), net GST payable

### Reporting
- **ATO myTax summary:** expenses grouped by ATO category, grand total, field-by-field myTax instructions tailored to Matt's situation (non-commercial losses, $0 income, correct schedule)
- **BAS report:** quarterly GST summary (dormant until GST registered, activates on registration date)

### Auth
- Single user, session-based login (Flask-Login)
- Admin user created at setup

---

## Out of Scope (v1)

- API integrations for Anthropic usage data, OpenAI, Fal.ai (PDF upload for these in v1; API integrations post-Railway)
- Multi-user / multi-tenant
- Mobile app
- Email invoice parsing
- Xero / MYOB / accounting software integration
- App Store / Play Store income tracking (deferred until income exists)
- Automated notifications or scheduled sync (manual sync trigger in v1)

---

## Key Risks & Open Questions

1. **Railway API stability** — GraphQL API is public but not versioned with SLA guarantees. Monitor for breaking changes.
2. **RBA exchange rate free tier** — 300 calls/month is ample for personal use. If it ever scales, switch to direct RBA RSS parsing (free, no limit).
3. **GST on USD services** — when GST-registered, the "reverse charge" mechanism technically applies to imported services from non-registered overseas suppliers. This is complex and often not enforced for small businesses but should be flagged in the BAS report as a known complexity.
4. **ATO rule changes** — non-commercial loss rules and sole trader tax treatment could change. Tax logic should be clearly separated in the codebase so it can be updated without touching the data layer.
5. **Invoice PDF storage growth** — storing PDFs as BYTEA in PostgreSQL is fine for ~100 invoices/year. Worth monitoring if the vendor list grows significantly.

---

## Success Criteria

- Matt can complete his annual ATO tax return using only data from this app — no separate spreadsheet needed
- Every deductible expense is captured, has a PDF attached, and is correctly converted to AUD
- The GST transition is smooth: entering the registration date changes the app's behaviour from that point forward with no data loss
- At tax time, the report page tells Matt exactly which dollar amount to enter in which myTax field
- The app takes less time to maintain than the problem it solves

---

*Product Design completed: 24 May 2026*
*Next stage: Branding — visual identity, colour palette, typography, logo direction*
