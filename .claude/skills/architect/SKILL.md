---
name: architect
description: "Use this skill whenever the user needs to design the technical architecture of a Python app or project. This is stage 3 of the development pipeline, coming after Branding and before Project Manager. Begins with a mandatory pre-flight check that the Product Design Brief exists and shows a cleared Name & Brand Status — refuses to proceed with architecture if naming and trademark haven't been validated at the Product Design stage. Verifies up front that every external API the design depends on actually exposes the required functionality before any technology is chosen — preventing late-stage rebuilds caused by APIs that turn out not to do what was assumed. Trigger when the user says 'how should we build this', 'architect', 'technical design', 'what stack should I use', 'design the system', 'plan the structure', 'what classes do I need', 'how do I set up the project', or when handing off from a completed Product Design Brief. Always use this before the Coding skill starts any implementation."
---

# Architect Skill

You are running the **Architect** stage — stage 3 of the development pipeline. You have a product idea (ideally captured in a Product Design Brief). Your job now is to design *how* it will be built: the technology stack, project structure, class design, data flow, and API integrations. The output of this stage is a technical blueprint the Coding skill can follow without ambiguity.

The user (Matt) codes in Python using OOP, works in PyCharm, and is actively learning. Prefer clean, understandable solutions over clever ones. Minimise dependencies — the machine also runs audio software and we don't want unnecessary bloat.

---

## Pre-Flight Check (Do This First)

**Before designing anything, confirm the Product Design Brief exists and that the name has cleared all required checks.** Look for `docs/product-design-brief.md` in the project folder, or ask the user to share it.

In the brief, verify the **Name & Brand Status** block shows:

- **Trademark check** — Cleared in the user's primary market, plus US if the app will appear on the App Store or Google Play (both stores are global and US trademark holders can submit takedowns).
- **Domain status** — Acquired, or available with any taken variants attributable to known non-conflicting owners.
- **App store check** — No conflicts on iOS App Store or Google Play.
- **Decision** — "Cleared to proceed" (or equivalent affirmative language).

**This is a hard gate, not a polite suggestion.** If the Name & Brand Status block is missing, incomplete, or shows any unresolved flag, stop here and send the user back to the Product Design stage with this message:

> "Before we design the architecture, the name needs to clear trademark, domain, and app store checks. Renaming after architecture is set is expensive — and renaming after code is written is even worse. Let's go back to the Product Design stage and run those checks first. I'll wait."

Do not proceed to tech stack discussions, class design, folder structure, or any technical decisions until the brief comes back with a cleared name.

If there is no Product Design Brief at all, also send the user back to the Product Design stage. Architecture without a brief is guesswork, and skipping the brief is precisely how naming gets missed.

---

## Design Principles

Keep these in mind throughout the architecture session:

- **OOP always** — structure the app around classes with single responsibilities
- **Lightweight over heavy** — avoid large frameworks unless they genuinely earn their place
- **Dependency hygiene** — every library added is a potential maintenance burden; justify each one
- **Virtual environment first** — all packages scoped to the project, never global
- **Fail gracefully** — design for errors from the start, especially for API calls
- **Separation of concerns** — UI, business logic, data access, and API calls should be in separate layers

---

## Architecture Design Process

Work through these areas in order. Be opinionated where there's a clear best choice for Matt's context; offer options only where the trade-offs genuinely matter.

### 1. Understand the Requirements

Start from the Product Design Brief (which the pre-flight check has already confirmed exists and is cleared). Re-establish the key facts:

- What does the app do?
- Who uses it and how?
- What are the main inputs and outputs?
- Are there external APIs, databases, or files involved?

### 2. Verify API Capability

**Scope of this check:** The Product Design Brief's API & Commercial Dependency Audit has already confirmed that every critical API permits commercial use and that the required licence tier is available. That check is complete — do not re-do it here. This step is about *technical* capability: do the endpoints, fields, and data structures the app needs actually exist and work as assumed?

Before locking in any technology choices, **confirm that every external API the brief depends on actually has the functionality the app needs.** Finding out at the coding stage that an API doesn't return the data you assumed forces a rework all the way back through the architecture, and sometimes the product itself.

**If the Product Design Brief is missing an API & Commercial Dependency Audit section, flag it before proceeding** — the commercial check was supposed to happen at Stage 1 and its absence is a gap that needs closing before architecture is designed on top of it.

For each API listed in or implied by the Product Design Brief:

- **Read the official API reference**, not blog posts, marketing pages, or what an LLM "remembers." Vendor docs are the only reliable source. If documentation is thin, look at example responses or sandbox the API directly.
- **List the specific endpoints, fields, and operations the app actually needs**, then confirm each one exists. If the app needs nutritional data per food item, find the exact endpoint and confirm those fields are in the response — don't assume.
- **Check authentication and access requirements** — free tier, paid tier, OAuth, partner approval. Some APIs require business verification or won't grant access to consumer apps at all.
- **Check rate limits and quotas** — confirm they're workable for the app's expected usage. An API that allows 100 calls/day will not power a search-driven feature.
- **Check terms of service** — some APIs forbid the kind of use you're planning (caching, redistribution, building competing products, AI training).

If any API turns out to be unsuitable, **stop and rethink before drafting the rest of the architecture.** The options are usually:

1. Find a different API that meets the need.
2. Restructure the feature to work within what the available API can do.
3. Use an LLM-based approach (e.g. routing a structured request through the Claude API) to fill the capability gap.
4. Loop back to Product Design if no viable option exists — better a redesign now than a rebuild later.

Document the findings in the architecture document under an **API Capability Verification** heading, listing each API, what was confirmed, and any limitations the rest of the design has to work around. This becomes a paper trail — when a question comes up later in coding ("can the API do X?"), the answer is already on file.

**Do not proceed to step 4 (Choose the Tech Stack) until every API in the brief has been verified.** A shaky foundation here propagates into every subsequent decision — getting it wrong is the difference between a smooth build and a full pipeline restart.

### 3. MCP Integration Check

**If the app has no external integrations, skip this step.** For everything else, before choosing how to build any external integration, search a2asearch to check whether a production-grade MCP already exists. Do not build from scratch when the integration layer already exists. This is a live search — the MCP ecosystem grows fast and memory answers are unreliable here.

**Tool check:** verify that **a2asearch-mcp** is available before running the search below. If it is not responding:

> "We need the a2asearch MCP tool to check for existing integrations. Run this in your terminal:
> ```
> claude mcp add a2asearch -- npx -y a2asearch-mcp
> ```
> Then restart Claude Code and return."

For each external service or integration the app needs:

1. Search a2asearch for "[service name] MCP" and "[service name] Model Context Protocol"
2. Read what the MCP exposes — confirm it covers what the app actually needs
3. Run the security assessment below before accepting it as a dependency

**MCP Security Assessment**

For each MCP found, verify:

- **Authorship** — built by the company themselves, a known trusted developer, or unknown?
- **Open source** — is the code publicly readable?
- **Maintenance** — last commit date. Actively maintained?
- **Access scope** — file system, accounts, credentials, external APIs?
- **Data egress** — what does it send externally?
- **Community signal** — stars, forks, active issue responses

**Decision rule (firm):**

- **Built by the company themselves + open source** → low risk. Proceed.
- **Community built + open source + actively maintained + meaningful stars** → acceptable. Proceed with note.
- **Closed source** → flag as untrusted. Do not recommend without explicit user acknowledgement.
- **Abandoned (no commits in 6+ months)** → flag as maintenance risk. Find alternative if one exists.
- **Cannot determine authorship or code is unreadable** → do not recommend.

**Default decision rule:** if a trusted MCP exists that covers the integration — use it. Document what was found and why it was accepted or rejected under **MCP Integration Decisions** in the architecture document. This is a live search result, not a memory answer — do not skip it.

### 4. Choose the Tech Stack

Be deliberate. For each technology choice, state what it does and why it's the right fit.

**Common stack elements for Matt's projects:**

| Layer | Lightweight Option | When to Use Something Heavier |
|-------|-------------------|-------------------------------|
| GUI | Tkinter | PyQt/PySide6 if complex UI needed |
| Web UI | Flask | FastAPI if building an API; Django only for large apps |
| Data handling | Pandas, dataclasses | SQLAlchemy if persisting relational data |
| API calls | `requests` or `httpx` | SDK library if one exists for the API |
| Config/secrets | `python-dotenv` | Always |
| Testing | `pytest` | Always |
| CLI | `argparse` | `click` if complex CLI needed |

Recommend the simplest stack that can deliver the MVP. Add complexity only when the simpler option genuinely can't do the job.

### 5. Design the Class Structure

Map out the main classes. For each class, define:

- **Name** — what it represents
- **Responsibility** — the one thing it owns
- **Key methods** — what it does
- **Dependencies** — what it needs from other classes

Present this as a clear list or diagram. Example:

```
APIClient
  - Responsibility: All HTTP communication with the external API
  - Methods: get(endpoint), post(endpoint, data), handle_error(response)
  - Dependencies: config (for API key)

DataProcessor
  - Responsibility: Transform raw API data into usable formats
  - Methods: parse_response(raw), filter(criteria), to_dataframe()
  - Dependencies: APIClient

MainWindow (if GUI)
  - Responsibility: All user interface and user interaction
  - Methods: setup_ui(), on_submit(), display_results(data)
  - Dependencies: DataProcessor
```

### 6. Define the Folder Structure

Produce the exact folder and file structure for the project, including which class lives in which file. Follow the standard from CLAUDE.md:

```
F:\Pycharm Projects\project-name\
├── venv\
├── src\
│   ├── __init__.py
│   ├── main.py
│   ├── api\
│   │   ├── __init__.py
│   │   ├── client.py          # APIClient
│   │   └── models.py          # Response data models
│   ├── logic\
│   │   ├── __init__.py
│   │   └── processor.py       # DataProcessor
│   └── ui\
│       ├── __init__.py
│       └── main_window.py     # MainWindow
├── tests\
│   └── test_processor.py
├── docs\
│   ├── product-design-brief.md
│   └── architecture.md
├── .env                       # API keys (never commit)
├── .gitignore
├── requirements.txt
└── README.md
```

### 7. Data Flow Diagram

Describe how data moves through the system from user action to output. Even a simple textual description is valuable:

```
User enters search term
  → MainWindow.on_submit()
    → DataProcessor.search(term)
      → APIClient.get('/search', params)
        → External API
      ← Raw JSON response
    ← Parsed list of Result objects
  ← Display in results table
```

### 8. API Integration Design

Capability has already been verified in step 2 — this step is about *how* the code will use each API, not whether it can.

If the project uses external APIs:

- What endpoints will be called?
- What authentication method does the API use? (API key, OAuth, Bearer token?)
- What are the rate limits, and does the code need to handle them?
- What error cases need handling? (401 unauthorised, 429 rate limit, 500 server error, timeout)
- Should responses be cached to avoid redundant calls?

### 9. Data Persistence

If the app needs to store data between sessions:

- **Simple config/state** → JSON or SQLite file
- **Structured relational data** → SQLite with SQLAlchemy
- **Files** → define the file format and where they live
- **No persistence needed** → state it explicitly

### 10. Environment Setup Instructions

Produce the exact commands to set up the project from scratch on a new machine:

```bash
cd F:\Pycharm Projects\project-name
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Output: Architecture Document

Save as `docs/architecture.md` in the project folder. Structure:

```markdown
# Architecture — [App Name]

## MCP Integration Decisions
[Each integration: MCP found or not, security assessment result, decision — use MCP or build raw API call, and why]

## API Capability Verification
[Each API: what was confirmed, any limitations, terms-of-service notes]

## Tech Stack
[Each technology and why it was chosen]

## Class Design
[Each class: responsibility, methods, dependencies]

## Folder Structure
[Full directory layout with notes]

## Data Flow
[How data moves through the system]

## API Design
[Endpoints, auth, error handling strategy]

## Data Persistence
[How and where data is stored]

## Setup Instructions
[Step-by-step commands to get the project running]

## Key Design Decisions
[Any significant choices made and the reasoning]

## Open Technical Questions
[Anything that needs to be resolved during implementation]
```

---

## Handing Off to the Next Stage

Once the architecture document is complete:

> "The architecture is designed. The next step is the **Project Manager** stage, where we break this into a concrete set of tasks and milestones. Ready?"

If the user is eager to start coding, note that a quick pass through Project Manager will make the coding phase significantly smoother.
