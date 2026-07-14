import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "coding_performance.db"


class Config:
    """Base configuration for the Coding Performance Analytics Dashboard."""

    # Flask configuration
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key-change-this-before-deployment",
    )

    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATABASE_PATH.as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security-Too configuration
    SECURITY_PASSWORD_SALT = os.getenv(
        "SECURITY_PASSWORD_SALT",
        "development-password-salt-change-this-before-deployment",
    )

    SECURITY_PASSWORD_HASH = "argon2"
    SECURITY_PASSWORD_LENGTH_MIN = 8

    # Authentication token configuration
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"

    # Token expires after 24 hours.
    SECURITY_TOKEN_MAX_AGE = 60 * 60 * 24

    # Custom authentication routes are used.
    SECURITY_REGISTERABLE = False
    SECURITY_CONFIRMABLE = False
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = False
    SECURITY_TRACKABLE = False

    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_RETURN_GENERIC_RESPONSES = True

    # The backend uses token authentication instead of form/session CSRF.
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True
    WTF_CSRF_ENABLED = False

    # Vue development server
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    JSON_SORT_KEYS = False