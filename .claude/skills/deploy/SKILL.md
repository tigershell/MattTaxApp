---
name: deploy
description: "Use this skill when the user needs to deploy a Python app to a server, cloud platform, or hosting environment. This is stage 7 of the development pipeline. Trigger when the user says 'deploy', 'host this', 'put it online', 'make it live', 'deploy to the cloud', 'how do I host this', 'set up a server', 'production', 'Railway', 'Render', 'AWS', 'Heroku', 'VPS', or when the app is ready to be made accessible to users. Also use when setting up environment configs, CI/CD basics, or production-ready configuration."
---

# Deploy Skill

You are running the **Deploy** stage — stage 7 of the development pipeline. The code is built and QA'd. Your job now is to get it running in a production environment where real users can access it.

Matt is a solo developer learning as he goes. Prioritise solutions that are straightforward to set up and don't require complex infrastructure. The machine is also a DAW, so local server hosting is not preferred — use cloud services.

---

## Before Deploying

Check these are in order before touching a server:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] QA has been run and critical issues are resolved
- [ ] No secrets hardcoded — all in `.env` and `.gitignore`
- [ ] `requirements.txt` is up to date and accurate
- [ ] README has setup instructions
- [ ] Code is committed and pushed to `main` branch on GitHub
- [ ] Version is tagged: `git tag -a v1.0.0 -m "First release"`

If any of these are missing, address them first.

---

## Choosing a Hosting Platform

Recommend the simplest platform that fits the app type. Don't over-engineer.

| App Type | Recommended Platform | Why |
|----------|---------------------|-----|
| Python web app (Flask/FastAPI) | **Railway** or **Render** | Simple GitHub-connected deploys, free tier available |
| API-only backend | **Railway** or **Fly.io** | Lightweight, fast setup |
| Desktop app (Tkinter/PyQt) | **Package for download** | No server needed — distribute as executable |
| Data tool / script | **Run locally or Railway** | Depends on whether users need a UI |
| App with a database | **Railway** (includes Postgres) | Managed DB + app in one place |
| MCP server | **Distribute as a local package** | MCP servers run on the user's machine — see Option D |

For most of Matt's early projects, **Railway** is the recommended starting point — GitHub integration, automatic deploys on push, easy environment variable management, and a free tier.

---

## Deployment Guides

### Option A: Railway (Recommended for web apps)

**What it is:** Cloud platform that connects to GitHub and deploys automatically on every push to main.

**Setup steps:**

1. Create account at railway.app
2. New Project → Deploy from GitHub repo → select your repo
3. Railway auto-detects Python; verify it found the right start command
4. Add environment variables in Railway dashboard (Settings → Variables) — copy from your `.env` file
5. Add a `Procfile` if Railway doesn't auto-detect the start command:
   ```
   web: python src/main.py
   ```
6. Deploy — Railway builds and runs the app

**Persistent storage note:** Railway's filesystem is ephemeral (resets on redeploy). If the app needs to persist files, use a database (Railway includes Postgres) or an object store (Cloudflare R2, AWS S3).

---

### Option B: Render

Similar to Railway. Good alternative if Railway's free tier is insufficient.

1. Connect GitHub repo at render.com
2. New → Web Service → select repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python src/main.py`
5. Add environment variables in the Render dashboard

---

### Option C: Desktop App Packaging (no server needed)

If the app is a desktop GUI (Tkinter, PyQt), package it as a standalone executable that users download and run.

**Using PyInstaller:**

```bash
pip install pyinstaller
pip freeze > requirements.txt

# Basic build
pyinstaller --onefile --windowed src/main.py

# With app icon
pyinstaller --onefile --windowed --icon=assets/icon.ico src/main.py
```

Output is in `dist/` — a single `.exe` file users can download and run with no Python needed.

**Important PyInstaller notes:**
- Test the built `.exe` on a clean machine (not the dev machine where everything is installed)
- Hidden imports may need specifying if dynamic imports are used
- `.env` files won't work the same way — use a config file or prompt for settings on first run

---

### Option D: MCP Server Distribution

**Check this section if the architecture type is "MCP server" or "Hybrid".** MCP servers do not deploy like web apps — they run as a local process on the user's machine and communicate with Claude Desktop or Claude Code via stdio. Railway, Render, and PyInstaller are the wrong tools here.

---

**How MCP servers are distributed:**

The user installs the server on their own machine and registers it in their Claude Desktop or Claude Code config. There are two standard patterns:

**Pattern 1 — Python package (recommended for Python MCP servers)**

Package the server so users can install it with `pip` or `uvx`:

1. Add a `pyproject.toml` or `setup.py` to the project root
2. Publish to PyPI (or distribute a wheel directly)
3. User installs: `pip install your-mcp-package` or `uvx your-mcp-package`
4. User adds to their Claude Desktop config (see below)

**Pattern 2 — Direct script (simpler, good for early distribution)**

Share the `src/main.py` directly (or via GitHub). User clones or downloads the repo, installs requirements, and points their config at the script.

---

**Claude Desktop config — what the user needs to add:**

The user adds an entry to their `claude_desktop_config.json` file. On Mac this is at `~/Library/Application Support/Claude/claude_desktop_config.json`. On Windows it is at `%APPDATA%\Claude\claude_desktop_config.json`.

**Pattern 1 (installed package with uvx):**

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "uvx",
      "args": ["your-mcp-package"]
    }
  }
}
```

**Pattern 2 (direct script):**

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "python",
      "args": ["C:\\path\\to\\project\\src\\main.py"]
    }
  }
}
```

With environment variables (API keys etc.):

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "python",
      "args": ["C:\\path\\to\\project\\src\\main.py"],
      "env": {
        "API_KEY": "the-api-key-value"
      }
    }
  }
}
```

After adding the config, the user restarts Claude Desktop. The server appears in the tools list.

---

**Verify it is working:**

Before telling the user the deploy is done, test the server end-to-end:

```bash
# Run the MCP inspector to confirm tools are registered correctly
mcp dev src/main.py
```

Then test in Claude Desktop by asking Claude to use one of the server's tools by name. Confirm the tool executes and returns the expected output.

---

**For Claude Code (not Claude Desktop):**

Users add the server via the CLI:

```bash
claude mcp add your-server-name -- python /path/to/src/main.py
```

Or for a uvx-installed package:

```bash
claude mcp add your-server-name -- uvx your-mcp-package
```

---

**Note on hosted MCP servers (HTTP/SSE transport):**

If the architecture specifically calls for a hosted MCP server (accessible over the internet rather than running locally), this can be deployed to Railway or Render — but the server must be built with HTTP/SSE transport, not stdio. This is a more advanced pattern; confirm with the architecture document before choosing this path.

---

## Environment Configuration for Production

Production needs different config from development. Use environment variables for everything that changes between environments.

```python
import os
from dotenv import load_dotenv

# Only load .env in development (not in production where env vars are set directly)
if os.path.exists('.env'):
    load_dotenv()

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('API_KEY')
```

Never put development values in production and never commit `.env` files.

---

## Monitoring & Logging

Once live, you need to know if it's working:

- Set log level to `INFO` in production (not `DEBUG` — too noisy)
- Railway and Render both have built-in log viewers — check them after deploy
- For serious production apps, add error alerting (Sentry has a free tier):

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
```

---

## Custom Domain (optional)

If the app needs a proper domain (e.g., myapp.com):

1. Buy domain from Namecheap or Cloudflare Registrar
2. In Railway/Render: Settings → Custom Domain → enter domain
3. Add CNAME record in domain DNS settings pointing to the platform's URL
4. Wait up to 24h for DNS propagation
5. SSL is handled automatically by Railway/Render

---

## Deployment Checklist

Before declaring done:

- [ ] App runs correctly on the production URL
- [ ] All environment variables are set in the hosting dashboard
- [ ] No sensitive data in the logs
- [ ] Test the critical user flow end-to-end on production
- [ ] Note the production URL in the README
- [ ] Version tagged and pushed to GitHub

---

## Output: Deployment Notes

Save as `docs/deployment.md`:

```markdown
# Deployment — [App Name]

## Production URL
[URL here]

## Platform
[Railway / Render / PyInstaller / other]

## Environment Variables Required
[List of env var names (not values) needed in production]

## Deploy Process
[How to redeploy — manual steps or automatic on push]

## Monitoring
[Where to check logs, any alerting set up]

## Known Production Differences
[Anything that behaves differently in production vs development]
```

---

## Handing Off

Once live:

> "The app is deployed and running at [URL]. Final step in the pipeline is **Sales & Marketing** — getting it in front of users. Ready to move there?"
