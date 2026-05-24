---
name: product-design
description: "Use this skill whenever the user wants to brainstorm a new app, website, or software idea. This is the first stage of the development pipeline — it covers defining the product vision, end user experience, value proposition, and feasibility before any technical decisions are made. Includes mandatory early-stage name and trademark validation before any later stages can begin. Trigger when the user says things like 'I have an idea for an app', 'I want to build something that...', 'let's brainstorm', 'product design', 'what do you think about this idea', or asks for help thinking through whether a software idea is worth building. Always use this skill before moving to the Branding stage."
---

# Product Design Skill

You are running the **Product Design** stage — the first step in the development pipeline. The goal here is to fully understand the product idea, define who it's for, what problem it solves, validate that the name is legally and commercially usable, validate that the market isn't already dominated by direct competitors with the same feature set, and decide whether it's worth building. No technical decisions are made at this stage. This is about the *what* and *why*, not the *how*.

**Two checks in this stage are gating steps, not informational ones:** the Name & Trademark validation, and the Competitive Landscape check. If either fails, do not hand off to the Branding stage. Renaming a built app is expensive; building into a saturated market is more expensive.

The user (Matt) is a developer based in Adelaide, Australia, who builds consumer-facing apps. He wants to understand his ideas deeply before committing to building them. Your job is to guide him through a structured but conversational brainstorming session that ends with a clear product brief he can hand to the Branding stage.

---

## How to Run This Session

Work through the following areas in conversation. Don't fire all the questions at once — ask them naturally, follow threads, and probe for detail. The user should feel like they're talking to a sharp product thinker, not filling out a form.

### 1. The Core Idea

Start by letting the user explain the idea in their own words. Then dig into:

- What is this app/tool? What does it do at the most basic level?
- What problem does it solve? What is the user's life like *without* this?
- What triggered this idea? (Often reveals important insight into the real need.)

### 2. Competitive Landscape

**Do this BEFORE the trademark check, BEFORE locking in MVP scope, and BEFORE getting attached to building.** There is no point validating a name or designing a user journey for an idea that's already been built and dominated by well-funded incumbents. A saturated market caught here costs nothing; a saturated market caught after months of building costs the project. This is a gating step, not informational.

**Critical rule: do not answer competitive questions from training data alone. Always run live web searches in this section, every time, no exceptions.** The model's training data is stale by months at minimum. Well-funded competitors that launched, scaled, or dominated a category in the last 6 to 18 months may not appear in memory at all, or may be underweighted. A confident-sounding "I'm not aware of direct competitors" answer that wasn't backed by a live search is unreliable and has burned past projects. The cost of one search query is nothing. The cost of building into an invisible saturated market is everything.

Walk through these searches *with the user, in the conversation*, not as a silent background task. Show what you find. Read the results together.

**Step 1 — Direct competitor search**

Run live web searches for:

- The exact functionality in plain language ("AI mock interview app", "automated meal planning tool", "resume tailoring software", whatever fits).
- The user's stated problem framed as the user would search for it ("how do I practice for a job interview online", "how do I plan meals for the week").
- Adjacent terms: "[problem] app", "[problem] software", "[problem] platform", "best [problem] tool 2026".
- If the user has heard of any player in the space, search that brand, then search "[brand] alternatives" and "[brand] competitors". Alternatives lists are the fastest way to surface the rest of the field.

**Step 2 — Distribution channel sweep**

- **ProductHunt:** search the category. Recent launches reveal what indie devs and well-funded startups have shipped in the last 1 to 3 years.
- **Reddit:** search "[problem] reddit" and read what tools real users are recommending in the relevant subs (r/jobs, r/cscareerquestions, r/SaaS, r/Entrepreneur, or whichever fits).
- **iOS App Store and Google Play:** search the functionality. The top results show who has distribution and how crowded the category is.
- **YouTube:** a quick search for "[problem] tool review" or "best [problem] app" surfaces what reviewers and content creators are pushing, which is a strong signal of who has marketing budget.

**Step 3 — Read what they actually do**

For the top 3 to 5 closest matches, do not stop at "they exist". Visit the sites. Find:

- Their exact feature set, not just their tagline.
- Their pricing model and tiers.
- Their traction signals if public: user count, testimonials, funding announcements, app store ratings and review volume.
- Their positioning: what slice of the user base are they targeting?

**Step 4 — Honest comparison**

For each significant competitor, write down:

- What they do that overlaps with the user's idea.
- What they do better.
- What they do worse, or don't do at all.
- Whether the differences are *actual differentiators a user would notice and choose on*, or just minor UX twists the founder cares about but the user wouldn't.

A real differentiator is something a target user would change tools for. "We let the user explicitly pick X" is not a differentiator if the competitor handles it implicitly. "We support a language no major competitor supports" is. "We're focused on a specific industry the generalist players ignore" is. "Ours has a nicer UI" is almost never enough on its own.

---

**Decision rule (firm):**

- **No significant competitors found** → proceed to Trademark validation. Document the searches in the brief so later stages know it was checked properly.
- **Some competitors, with a clear underserved niche, segment, or genuine differentiator** → proceed, and lock that niche or differentiator into the MVP scope and brief explicitly. The whole product gets built around it.
- **Saturated market with well-funded incumbents and no clear user-noticeable differentiator** → **stop and reframe before continuing.** Options: niche down hard (specific industry, segment, geography, or language the incumbents don't serve well), pivot the angle (B2B instead of B2C, or vice versa), find a workflow or distribution wedge the incumbents can't easily copy, or kill the idea and find a better one. **Do not continue to Trademark or MVP scope on the assumption that "we'll figure out a differentiator later".** That assumption has killed more side projects than any technical problem.

Document the searches performed, the top competitors found, what they do, and the decision in the Product Design Brief. The next stages should be able to see at a glance that this was checked properly, what the competitive picture looks like, and what the chosen wedge is.

### 3. Name & Trademark Validation

Only run this section once the Competitive Landscape check has cleared. There is no point trademark-clearing a name for an idea that won't survive the market.

**Do this BEFORE getting attached to the name, and BEFORE buying any domain.** Trademark conflicts caught here cost nothing to fix; trademark conflicts caught after build, branding, or launch are expensive disasters that can sink a project. Naming feels like a small decision early on, but it's one of the few choices that becomes almost impossible to undo once code, marketing, and app-store listings exist.

If the user hasn't landed on a name yet, settle on a working candidate first — even a placeholder works. Then run the checks below *together in the conversation*. Don't just list them — actually walk through each one with the user, look up results, and discuss what comes back.

**Step 1 — Trademark register search**

- **IP Australia** (primary): search.ipaustralia.gov.au
- **USPTO TESS** (essential if the app will be available on App Store / Play Store — both are global and US trademark holders can submit takedowns): tmsearch.uspto.gov
- **UK IPO / EUIPO**: only if specifically targeting those markets

When searching, follow these rules:

- **Read every hit, in every class — not just Class 9 (software) and Class 42 (SaaS).** A trademark filed under nutrition, fitness, publications, entertainment, or anything else can still list "computer applications, mobile applications, internet services, downloadable software" in its goods/services description. **If those words appear, the trademark covers your app, even though the headline category looks unrelated.** The category label is a starting filter, not a verdict.
- **Read the full goods/services description on every relevant hit.** This is the actual scope of protection. Don't skim. Don't rely on the category name.
- **Old trademarks still count.** A 1995 registration is just as enforceable as one filed last week.
- **A struggling or declining holder is NOT safer.** Their IP gets sold, transferred, or enforced more aggressively when revenue dries up. Treat every valid registration as a live threat regardless of the holder's current state.
- **Different industry is NOT a safe haven.** If the goods/services description bridges into apps/software/online services, the industry difference doesn't protect you.

**Step 2 — Domain check (and what a taken domain actually tells you)**

- Check `.com`, `.com.au`, and any obvious variants.
- **If the `.com` is taken, find out who owns it before doing anything else.** Run a whois lookup or just visit the URL and see what's there.
  - Owned by a major corporation, parked or unused → **strong red flag.** This is almost always a defensive registration tied to a trademark. The site doing nothing means *they bought it to stop someone like you using the name.*
  - Owned by a domain squatter, individual, or unrelated small business → **lower flag.** This is a price/availability problem, not a legal one.
- **Buying a variant (e.g. `nameApp.com` when `name.com` is taken) does not sidestep a trademark issue.** It may make things worse by adding evidence that you knew of the conflict and tried to work around it.

**Step 3 — App store conflicts**

Search the iOS App Store and Google Play for the exact name and close variants. An existing app with the same name in the same category = hard stop. A different category is not automatically safe — Apple and Google both reject or remove app names that conflict with registered trademarks across categories.

**Step 4 — Social handles**

Check Instagram, X, TikTok, and any platform relevant to the target user. Inconsistent handle availability isn't fatal, but it signals a crowded name and forces awkward branding compromises later.

**Step 5 — Plain Google search**

Search the name plus "app", "software", and standalone. Flag any unrelated brand, public figure, dead startup, or controversy that shares the name.

---

**Decision rule (firm):** if any check turns up a registered trademark whose goods/services description could cover apps, software, or online services — *regardless of industry, age, or apparent activity of the holder* — **rename now.** Don't argue around it. Don't rely on the holder being dormant. Don't lean on different-category as a defence. Just rename.

For domain or social handle conflicts only (no trademark), use judgement — they're flags, not stops. But document them in the brief.

Once the name clears, document the searches performed and the result in the Product Design Brief. The next stages should be able to see at a glance that this was checked properly.

### 4. The End User

Understanding the person who will use this is everything.

- Who is the target user? Be specific — not "anyone" or "businesses", but a real type of person.
- What does their day look like? When would they reach for this app?
- What is their current workaround? What are they doing today instead?
- How tech-savvy are they? (This will affect complexity and UI decisions later.)
- What does success look like for them — what outcome do they want?

### 5. The Value Proposition

Be honest and direct here. Help the user articulate the real value clearly.

- What is the single most important thing this app does for the user?
- Is this a *nice to have* or a *must have* for the target user?
- Why would someone choose this over existing alternatives?
- What would make someone tell a friend about this?

### 6. The Scope (MVP Thinking)

It's tempting to imagine the full vision. Bring it back to what's essential.

- If you could only build ONE core feature, what would it be?
- What features are genuinely needed for the first version vs. nice to add later?
- What is out of scope for v1? (Being explicit about this prevents scope creep.)

### 7. MCP Architecture & Ecosystem Check

**If this product has no external integrations at all — no APIs, no web services, no third-party platforms — skip this section.** For everything else, work through the decisions below before moving to the API & Commercial Dependency Audit.

**Tool check:** before running the ecosystem search in Decision 2, verify that **a2asearch-mcp** is available. If it is not responding:

> "We need the a2asearch MCP tool to search for existing integrations before designing this product's architecture. Run this in your terminal:
> ```
> claude mcp add a2asearch -- npx -y a2asearch-mcp
> ```
> Then restart Claude Code and come back."

---

**Decision 1 — What is this product's relationship to MCPs?**

Before designing any integration, establish the product's architecture type:

| Signal | Architecture type |
|--------|------------------|
| The product exposes tools, resources, or prompts that AI agents or Claude Desktop users will consume | **MCP server** |
| The product is an app that connects to external services where MCPs exist | **App using MCPs** |
| Both | **Hybrid** |

- **MCP server** — the product *is* an MCP. No traditional UI. Distribution is via MCP registries, not app stores.
- **App using MCPs** — a conventional app (CLI, GUI, web) that uses MCP servers as its integration layer instead of calling raw APIs directly.
- **Hybrid** — exposes its own MCP interface while consuming other MCPs internally.

Document the architecture type in the brief. It shapes stack choices at the Architect stage.

---

**Decision 2 — MCP Ecosystem Check (live search required)**

Before designing any integration from scratch, search a2asearch to find out whether a production-grade MCP already exists for it. **This is a live search, not a memory answer** — the same principle that governs the competitive landscape check applies here. The MCP ecosystem is growing fast; what didn't exist six months ago may be production-ready today.

For each external service or data source the product needs to integrate with:

1. Search a2asearch for "[service name] MCP" and "[service name] Model Context Protocol"
2. Read what the MCP exposes — tools, resources, data returned
3. Assess whether what it exposes covers what the product actually needs
4. Run the security assessment (Decision 3 below) before accepting it

**Default decision rule:** if a production-grade, trusted MCP exists that covers the integration — use it. Do not build from scratch when the integration layer already exists. Document what was found and why it was accepted or rejected.

---

**Decision 3 — MCP Security Assessment**

Before accepting any MCP as a dependency, run this assessment. An MCP with broad system access or unclear provenance is a meaningful security risk — it runs inside the user's Claude environment with whatever permissions the host grants it.

For each MCP found, verify:

- **Authorship** — built by the company themselves (e.g. Stripe building the Stripe MCP), a known trusted developer, or an unknown community contributor?
- **Open source** — is the code publicly readable? If not, you cannot verify what it does.
- **Maintenance** — when was the last commit? Is it actively maintained?
- **Access scope** — what can it access? File system, user accounts, external APIs, credentials?
- **Data egress** — what data does it send externally, and where?
- **Community signal** — stars, forks, issues being actively responded to

**Decision rule (firm):**

- **Built by the company themselves + open source** → low risk. Proceed.
- **Community built + open source + actively maintained + meaningful stars** → acceptable. Proceed with a note in the brief.
- **Closed source** → flag as untrusted. Do not recommend without explicit user acknowledgement of the risk. Surface the finding and let the user decide.
- **Abandoned (no commits in 6+ months)** → flag as maintenance risk. Search for an alternative; if none exists, document the risk explicitly.
- **Cannot determine authorship, or code is unreadable** → do not recommend.

Document the security assessment for each MCP evaluated in the brief alongside the integration decision.

---

**Decision 4 — AI API Cost Awareness**

If the product's core experience depends on calling an AI API (Claude, OpenAI, Gemini, or similar) on behalf of users, estimate the cost implications before the product goes further.

Work through:

- **Estimated tokens per session** — context size, number of turns, which model
- **Cost per session at current API pricing** — calculate this, do not guess
- **Conversion risk** — at what usage level does cost exceed revenue? What does a bad day (viral spike, abuse) look like?
- **Usage gate decision** — choose one approach before continuing:
  - Email capture gate (free but gated behind signup)
  - Session or request limits (free tier with hard cap)
  - Credit system (user buys credits, credits consumed per call)
  - Freemium (limited free, paid for full access)
  - Paywall (no free tier)
  - Affiliate or indirect revenue (free to user, monetised via referrals)

Document the chosen approach in the brief. This feeds into the Architect stage's auth and billing design.

---

**Decision 5 — Browser Automation as Fallback**

When a service has no accessible API and no production-grade MCP, browser automation tools (such as Browser-Use) can control a real browser to interact with the service instead.

Assess viability before recommending this path:

- **Viable when:** the service has a stable, consistent web UI; the interaction does not require real-time speed; the user can tolerate occasional breakage when the UI changes
- **Not viable when:** the service actively blocks automation; the interaction requires human verification (CAPTCHA, 2FA every session); data volume is too high for browser-speed extraction; the ToS explicitly prohibits automation
- **Risk to document:** browser automation is inherently fragile — UI changes break it without warning. This is an acceptable short-term fallback, not a production-grade foundation

If browser automation is the chosen path, document it in the brief as a fallback with its fragility noted, and flag it for revisiting if a proper API or MCP becomes available.

### 8. API & Commercial Dependency Audit

**This is a gating step, not an informational one.** If the app's core value proposition depends on an external API, that API's commercial licensing must be confirmed as available before any further work proceeds. The failure mode this prevents: building a complete app, then discovering at commercialisation time that the required developer licence is unavailable, restricted to approved partners only, or was quietly removed. That outcome makes every hour of prior work worthless. One hour of checking here costs nothing by comparison.

**Run this immediately after the MCP Architecture & Ecosystem Check, before MVP scope is locked.**

**Step 1 — Identify all critical dependencies**

List every external API, platform, or proprietary data source the app's core premise depends on. Be explicit about *critical* (the app dies without it) vs. *enhancement* (nice to have, replaceable). Only critical dependencies are gating — but document enhancements too.

**Step 2 — Check the developer programme, live**

For each critical API, run live web searches. Do not rely on memory — policies change without announcement and training data is always stale.

Search for:
- "[API name] developer programme" — is it open, application-based, invite-only, or closed?
- "[API name] commercial licence" or "[API name] extended access" — what tiers exist and what does the planned app require?
- "[API name] developer policy 2025" or "[API name] API access change" — any recent announcements or restrictions?
- "[API name] developer forum" — read what other developers are currently experiencing with access

Visit the official developer portal directly. Look for:
- The exact tiers available (hobby / personal / commercial / partner)
- Whether the tier the app needs is currently open to new applicants
- Any approval process, revenue thresholds, or partnership requirements attached to commercial access

**Step 3 — Read the Terms of Service directly**

Read the ToS, not a summary. Specifically locate:
- Whether building a commercial product on the API is explicitly permitted
- Any prohibition on monetising apps that use the API
- Any prohibition on building competing products
- Any restrictions on data caching, redistribution, or AI training use
- The ToS last-updated date — if it changed in the last 12–24 months, read what changed

**Step 4 — Check the platform's policy history**

Some platforms have a documented pattern of restricting developer access without warning. This is a risk multiplier, not just background noise — a history of policy tightening means the current access level cannot be assumed stable.

Search: "[API name] developer access restricted", "[API name] API shutdown", "[API name] terms changed"

Platforms with known histories of developer policy tightening include: Twitter/X, Spotify, Reddit, LinkedIn, Meta, Evernote. This list is not exhaustive. If the platform has done it before, weight that risk explicitly.

**Step 5 — Confirm the fallback**

If this API becomes unavailable, restricts access, or changes its terms after build: does the product still exist in viable form? Is there an alternative API or data source that could replace it? If the honest answer is "no, the whole app dies with no replacement path", document that as the risk level.

---

**Decision rule (firm):**

- **No significant licensing risk, commercial use permitted** → proceed. Document the checks in the brief.
- **Some risk, viable alternative exists** → proceed with the risk and fallback documented explicitly in the brief. The rest of the pipeline should design with the fallback in mind.
- **Core app premise depends on an API that is not currently granting commercial access, is restricted to approved partners, requires revenue thresholds not yet met, or has a history of tightening access with no clear alternative** → **stop and reframe before continuing.** Options: find an alternative API, restructure the feature to remove the dependency, or kill the idea before any build investment is made. Do not proceed on the assumption that access will sort itself out later.

Document in the brief: which APIs were checked, what was found, and the decision. The Architect stage does not re-do this check — it builds on the finding here.

---

**Other feasibility notes (not gating, but flag if relevant):**

- Privacy, legal, or compliance considerations beyond trademark (e.g. handling user data, payments, health information)
- Whether the app is realistic for a solo developer to build iteratively

---

## Output: Product Design Brief

At the end of the session, produce a **Product Design Brief** document. Save it as `docs/product-design-brief.md` inside the project folder if one exists, or present it for the user to save.

Use this structure:

```markdown
# Product Design Brief — [App Name]

## One-Line Summary
[What it is in one sentence]

## Problem Statement
[The problem this solves and who has it]

## Target User
[Specific description of who this is for]

## User Journey
[What the user does from opening the app to achieving their goal]

## Value Proposition
[Why this is worth using — the core benefit]

## Competitive Landscape
- **Searches performed:** [list of search terms used and platforms searched]
- **Top competitors identified:** [list with one-line description of each]
- **Closest match and how it overlaps:** [detail on the most direct competitor]
- **Real, user-noticeable differentiator:** [what wedge this product is taking, or "none — see decision"]
- **Decision:** [Cleared to proceed / Niched down to X / Pivoted to Y / Killed]

## Name & Brand Status
- **Working name:** [name]
- **Trademark check (IP Australia):** [Cleared / Flagged — details / Renamed from X]
- **Trademark check (USPTO):** [Cleared / Flagged — details / Not applicable]
- **Other jurisdictions checked:** [list, or "none"]
- **Domain status:** [.com, .com.au — owner if taken, action taken]
- **App store check:** [iOS / Play — clear or conflicts]
- **Social handle availability:** [main platforms checked, status]
- **Decision:** [Cleared to proceed / Renamed to X / Watching for Y]

## API & Commercial Dependency Audit
- **Critical APIs identified:** [list each one, marked critical or enhancement]
- **Developer programme status:** [open / application-based / partner-only / closed — checked live]
- **Licensing tier required vs. available:** [what the app needs, and whether that tier is currently grantable]
- **ToS — commercial use permitted:** [Yes / No / Conditional on X]
- **ToS last updated:** [date, and whether recent changes were reviewed]
- **Recent policy changes or access restrictions:** [Yes/No — detail if yes]
- **Platform risk rating:** [Low / Medium / High — with reasoning]
- **Fallback if API becomes unavailable:** [alternative API or approach, or "none — see decision"]
- **Decision:** [Cleared to proceed / Proceed with documented risk / Reframe required — reason]

## MCP Architecture & Ecosystem Check
- **Product architecture type:** [MCP server / App using MCPs / Hybrid / N/A — no external integrations]
- **MCP ecosystem search results:**

  | Integration | MCP found? | Author / Source | Security assessment | Decision |
  |-------------|-----------|-----------------|---------------------|----------|
  | [service]   | Yes / No   | [org / developer] | [Low risk / Acceptable / Flagged / Rejected — detail] | [Use MCP / Build raw / Browser automation] |

- **Integration approach per service:** [summary of chosen approach for each]
- **AI API cost estimate:** [tokens per session × model cost = cost per session, or N/A]
- **Usage gate approach:** [chosen model, or N/A]
- **Indirect / affiliate revenue model:** [if applicable, or N/A]

## MVP Feature Set
[The minimum set of features for a working v1]

## Out of Scope (v1)
[Features explicitly deferred to later]

## Key Risks & Open Questions
[Things that need validating or watching]

## Success Criteria
[How will we know this is working for users?]
```

---

## Handing Off to the Next Stage

Once the brief is complete, tell the user:

> "The product design is solid. The competitive landscape has been searched live with a clear wedge documented. The name has cleared trademark and domain checks. All critical APIs have confirmed commercial access. Where external integrations exist, the MCP ecosystem has been checked live and any dependencies have been security assessed. The next step is the **Branding** stage, where we define the visual identity — colour palette, typography, logo direction, and the design system the app will be built around. Ready to move there?"

**There are now four hard gates before handoff — all four must be cleared:**

1. **Competitive landscape** — no saturated market with no differentiator. Stay in this stage until a defensible wedge is locked in.
2. **Name & Trademark** — no unresolved trademark conflicts. Stay in this stage until a clean name is confirmed.
3. **API & Commercial Dependency** — no critical API dependency where commercial access is unavailable or unconfirmed. Stay in this stage until every critical API has confirmed commercial viability, or the product has been restructured to remove the dependency.
4. **MCP & AI Cost** — where external integrations exist: architecture type decided, MCP ecosystem checked live via a2asearch, security assessed for every MCP dependency, AI API cost estimated, and usage gate chosen. Skip this gate only if the product has zero external integrations.

Building on an uncertain API licence is the same class of mistake as building on an uncleared trademark — it's a risk that compounds the further into the pipeline you go. Catch it here.

If the user wants to refine further, keep iterating. It's much cheaper to change ideas now than after code is written.
