import os


class DevelopmentConfig:
    """Local development — uses SQLite, debug mode on."""

    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///taxidermatt.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig:
    """Railway production — expects real env vars, no debug."""

    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def validate(cls) -> None:
        """Raise at startup if required env vars are missing."""
        if not cls.SECRET_KEY:
            raise EnvironmentError("SECRET_KEY not set")
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise EnvironmentError("DATABASE_URL not set")


# Maps the FLASK_ENV value to the right config class
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}