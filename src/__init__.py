import os
from flask import Flask
from .config import config_map, DevelopmentConfig
from .extensions import db, login_manager, migrate


def create_app() -> Flask:
    """App factory — creates and configures the Flask application.

    Reads FLASK_ENV to choose the right config class (development/production).
    Initialises extensions, registers all blueprints, and returns the app.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load the right config for the current environment
    env = os.getenv("FLASK_ENV", "development")
    config_class = config_map.get(env, DevelopmentConfig)
    app.config.from_object(config_class)

    # Wire extensions to this app instance
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"

    # Import models here so Flask-Migrate can discover them for migrations
    with app.app_context():
        from .models import user, document, expense  # noqa: F401

    # Register all blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.expenses import expenses_bp
    from .routes.vendors import vendors_bp
    from .routes.years import years_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(years_bp)
    app.register_blueprint(reports_bp)

    return app