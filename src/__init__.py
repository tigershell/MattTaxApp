import os
import logging
import click
from flask import Flask
from dotenv import load_dotenv
from .config import config_map, DevelopmentConfig
from .extensions import db, login_manager, migrate

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def create_app(config_overrides: dict | None = None) -> Flask:
    """App factory — creates and configures the Flask application.

    Reads FLASK_ENV to choose the right config class (development/production).
    Initialises extensions, registers all blueprints, and registers CLI commands.

    Args:
        config_overrides: Optional config values applied AFTER the base config
            but BEFORE extensions initialise. Tests MUST use this to point at an
            in-memory database — Flask-SQLAlchemy binds its engine inside
            db.init_app(), so changing app.config afterwards is ignored and the
            app would keep using the real configured database.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    env = os.getenv("FLASK_ENV", "development")
    config_class = config_map.get(env, DevelopmentConfig)
    app.config.from_object(config_class)
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "auth.login"

    # Import all models so Flask-Migrate can discover them for migrations
    with app.app_context():
        from .models import User, FinancialYear, Vendor, Expense, Income, RBARate, Document  # noqa: F401

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.expenses import expenses_bp
    from .routes.income import income_bp
    from .routes.upload import upload_bp
    from .routes.vendors import vendors_bp
    from .routes.years import years_bp
    from .routes.reports import reports_bp
    from .routes.backup import backup_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(years_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(backup_bp)

    _register_cli(app)

    return app


def _register_cli(app: Flask) -> None:
    """Register flask CLI commands."""

    @app.cli.command("seed")
    def seed():
        """Seed vendors and current financial year into the database."""
        from .logic.seeder import DatabaseSeeder
        seeder = DatabaseSeeder()
        vendors_created = seeder.seed_vendors()
        seeder.seed_current_financial_year()
        if vendors_created:
            print(f"Seeded {vendors_created} vendor(s).")
        else:
            print("Vendors already seeded — nothing to do.")
        print("Current financial year ensured.")

    @app.cli.command("create-admin")
    def create_admin():
        """Create the admin user from ADMIN_EMAIL and ADMIN_PASSWORD env vars."""
        from .models.user import User

        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        if not email or not password:
            print("Error: ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env")
            return

        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"User {email} already exists.")
            return

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user created: {email}")

    @app.cli.command("backup")
    def backup():
        """Create a timestamped backup of the database in the backups/ folder."""
        from .logic.backup_manager import BackupManager

        dest = BackupManager().create_backup()
        print(f"Backup created: {dest}")
        print("Tip: also copy this file somewhere off this drive (cloud/another disk).")

    @app.cli.command("restore")
    @click.argument("backup_file")
    def restore(backup_file):
        """Restore the database from a backup file.

        The current database is snapshotted first, so a restore cannot lose your
        present data. BACKUP_FILE may be a name in backups/ or a full path.
        """
        from .logic.backup_manager import BackupManager

        safety = BackupManager().restore(backup_file)
        print(f"Database restored from: {backup_file}")
        print(f"Previous database saved to: {safety} (use it to undo if needed).")
