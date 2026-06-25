import pytest
from src import create_app
from src.extensions import db as _db


@pytest.fixture
def app():
    """Create a test Flask app using an isolated in-memory SQLite database.

    The in-memory URI is passed THROUGH create_app (config_overrides) so it is
    applied before Flask-SQLAlchemy binds its engine. Setting app.config after
    create_app() does NOT work — the engine is already bound to the configured
    database, so tests would run create_all()/drop_all() against the real dev
    database and destroy live data.
    """
    test_app = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    """Provide the DB instance within the active app context."""
    yield _db