# Tax Tracker

A locally-deployed Flask web application for tracking Australian sole trader business expenses for the ATO tax return.

Upload PDF tax invoices → Claude API extracts the data automatically → expenses stored in PostgreSQL → end-of-year ATO summary generated.

## Stack

- **Flask** — web framework
- **PostgreSQL** — database (SQLite for local dev)
- **SQLAlchemy** — ORM
- **Anthropic Python SDK** — PDF data extraction via Claude API
- **Flask-Login** — single-user session auth
- **Railway** — deployment target

## Local Development

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (copy .env.example and fill in values)
# For local dev use: DATABASE_URL=sqlite:///dev.db

# 4. Initialise the database and create the admin user
flask --app "src:create_app()" shell
>>> from src.extensions import db
>>> db.create_all()
>>> from src.models.user import User
>>> u = User(email='mattacollis@gmail.com')
>>> u.set_password('yourpassword')
>>> db.session.add(u)
>>> db.session.commit()

# 5. Run
flask --app "src:create_app()" run
```

## Deployment

See `docs/tax-tracker-brief.md` for Railway deployment steps.

## Financial Year

2025–26 (1 July 2025 – 30 June 2026)