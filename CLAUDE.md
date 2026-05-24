# CLAUDE.md — Matt's Development Environment

This file defines the standards, conventions, and context for all of Matt's development projects. Reference this whenever starting or continuing any project.

---

## About Matt

Matt is an app developer building consumer-facing Python applications. He has a couple of years of experience using Python with AI assistance, primarily building Pandas-based business tools with GUI interfaces in PyCharm. He is also familiar with Databricks. He is actively learning — projects will often involve new technologies, APIs, and patterns, so Claude should explain reasoning clearly and not assume familiarity with advanced concepts.

Matt prefers an Object-Oriented Programming (OOP) approach to keep code modular, maintainable, and easy to extend. All code should follow OOP principles unless there is a strong reason not to.

---

## Machine Setup

- **OS:** Windows 11
- **Machine role:** Development workstation AND audio DAW (Digital Audio Workstation)
- **Critical constraint:** This machine runs audio recording software. System bloat, unnecessary background services, and global package installs can cause latency and performance issues with the DAW. Be conservative and mindful with anything that touches the system level.

### Drive Layout

| Drive | Purpose | Use for Projects? |
|-------|---------|-------------------|
| C: | Windows OS + system files | NO |
| D: | Audio recording storage | NO |
| F: | USB SSD — development storage | YES |

**All projects must be created under `F:\Pycharm Projects\`**. Never suggest or create project files on C: or D:.

---

## IDE & Tools

- **IDE:** PyCharm
- **Version Control:** Git + GitHub (Matt is mildly familiar — explain Git steps clearly)
- **Python package manager:** pip (inside virtual environments only)

---

## Project Standards

Every project must follow these standards without exception.

### Virtual Environments

Every project gets its own virtual environment. Never install packages globally.

```bash
# Create venv inside the project folder
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
```

PyCharm should be configured to use the project's local venv interpreter.

### requirements.txt

Every project must have a `requirements.txt` in the root. It must be updated every time a new package is installed.

```bash
pip freeze > requirements.txt
```

When adding a package, always:
1. Install it (`pip install package-name`)
2. Immediately update requirements.txt (`pip freeze > requirements.txt`)
3. Commit the updated requirements.txt with the code that uses it

### Project Folder Structure

```
F:\Pycharm Projects\
└── project-name\
    ├── venv\                  # Virtual environment (never commit this)
    ├── src\                   # All source code
    │   ├── __init__.py
    │   ├── main.py            # Entry point
    │   └── [modules]\         # OOP modules by responsibility
    ├── tests\                 # Unit and integration tests
    ├── docs\                  # Logic documentation, design notes
    ├── .gitignore             # Must include venv/, __pycache__/, .env
    ├── requirements.txt       # Always up to date
    └── README.md              # Project overview
```

### .gitignore (minimum required entries)

```
venv/
__pycache__/
*.pyc
.env
*.log
.idea/
```

---

## OOP Conventions

All code should be structured around classes with clear single responsibilities.

- Each class lives in its own file where practical
- Use `__init__` to set up state, not to do heavy work
- Prefer composition over deep inheritance
- Keep methods short and focused — if a method is doing two things, split it
- Use type hints on all method signatures
- Docstrings on every class and public method

**Example structure for an API-based app:**

```
src/
├── api/
│   ├── client.py         # APIClient class — handles all HTTP
│   └── models.py         # Data models / dataclasses
├── ui/
│   └── main_window.py    # MainWindow class — handles GUI
├── logic/
│   └── processor.py      # DataProcessor class — business logic
└── main.py               # Wires everything together
```

---

## Git Workflow

Matt is learning Git. Always explain what each command does and why.

### Branching Strategy (simple, for solo projects)

- `main` — stable, working code only
- `dev` — active development
- Feature branches: `feature/short-description`

### Commit Standards

Commits should be small and focused. Use this format:

```
type: short description

Examples:
feat: add user login screen
fix: handle empty API response
docs: update setup instructions
refactor: extract APIClient into its own class
test: add unit tests for DataProcessor
```

### Release Versioning

Use semantic versioning: `v1.0.0` (major.minor.patch)
- **patch** — bug fixes
- **minor** — new features, backwards compatible
- **major** — breaking changes or significant new releases

Tag releases in GitHub: `git tag -a v1.0.0 -m "First release"`

---

## API Projects

When working with external APIs:

- Store all API keys and secrets in a `.env` file (never hardcode, never commit)
- Use `python-dotenv` to load environment variables
- Always handle API errors gracefully — assume the API can fail
- Rate limiting: be aware of limits and implement retry logic where needed
- Log API calls and responses during development

```python
# .env file
API_KEY=your_key_here

# In code
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("API_KEY")
```

---

## Documentation Standards

Every project must maintain docs as it grows, not as an afterthought.

- `docs/logic.md` — explains non-obvious decisions, algorithms, data flows
- `docs/api_notes.md` — notes on any external APIs used (rate limits, quirks, gotchas)
- Inline comments for anything that isn't self-explanatory
- Update docs when code changes

---

## Skill Pipeline

Matt uses a structured skill pipeline for every project. Work flows through these stages in order:

| Stage | Skill | Purpose |
|-------|-------|---------|
| 1 | **Product Design** | Brainstorm the idea, define end user experience, validate value |
| 2 | **Branding** | Visual identity — colours, typography, logo direction, design system |
| 3 | **Architect** | Design the technical solution — stack, structure, data flow |
| 4 | **Project Manager** | Break into milestones and ordered tasks |
| 5 | **Coding** | Write code in OOP style, manage Git, maintain docs |
| 6 | **QA** | Review for correctness, efficiency, edge cases |
| 7 | **Deploy** | Package and host the application |
| 8 | **Sales & Marketing** | Get the app in front of users |

It's normal to loop back — e.g., QA findings may send you back to Coding, or Architect decisions may need Product Design input.

---

## New Project Setup

Every new project starts the same way. Do this before anything else.

1. Create the project folder in `F:\Pycharm Projects\project-name\` via PyCharm
2. Copy the contents of `F:\Pycharm Projects\CLAUDE_SKILLS\` into the new project folder
3. Open the project in PyCharm and open the built-in terminal
4. Run `claude` in the terminal
5. Say **"set up this project folder"** — Claude Code CLI will confirm the setup and you're ready to go
6. Start with the **Product Design** skill

Note: Cowork cannot access F: directly. All project work happens via Claude Code CLI in the PyCharm terminal. Cowork is used only for managing this setup project (CLAUDE.md, skills, admin).

---

## General Principles

- **Explain as you go.** Matt is learning. Don't just write code — explain the reasoning.
- **Don't bloat the system.** Prefer lightweight solutions. Avoid heavy frameworks unless necessary.
- **Keep it modular.** If something might be reused, make it a class or utility.
- **Fail gracefully.** Apps should handle errors without crashing. Log them.
- **Security basics.** No hardcoded secrets. Validate inputs. Don't expose sensitive data.
- **One thing at a time.** Small commits, small PRs, clear progress.
