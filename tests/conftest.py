import pytest
from src import create_app
from src.extensions import db as _db


@pytest.fixture
def app():
    """Create a test Flask app using an isolated in-memory SQLite database."""
    test_app = create_app()
    # Override the database URI BEFORE the first connection is made
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["TESTING"] = True

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    """Provide the DB instance within the active app context."""
    yield _db