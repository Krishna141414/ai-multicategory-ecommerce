"""
Django settings for the Chowk store.

All secrets and environment-specific values come from `.env` (see `.env.example`).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    """Read a true/false flag from the environment."""
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    """Read a comma-separated list from the environment."""
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing. Copy .env.example to .env and set it.")

DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Project apps
    "core",
    "accounts",
    "catalog",
    "orders",
    "reviews",
    "messaging",
    "recommender",
    "adminpanel",
    "testreports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.ActiveCustomerMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.store_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Databases -------------------------------------------------------------
# "default" holds all shop data. "reports" holds only automated-test results,
# so test runs never write into shop data (brief rule 7).
# IMMEDIATE transactions take SQLite's write lock at BEGIN, which serialises
# concurrent checkouts (select_for_update is a no-op on SQLite).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 20},
        "TEST": {"NAME": BASE_DIR / "test_db.sqlite3"},
    },
    "reports": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "reports.sqlite3",
        "OPTIONS": {"timeout": 20},
        "TEST": {"NAME": BASE_DIR / "test_reports.sqlite3"},
    },
}
DATABASE_ROUTERS = ["config.db_router.ReportsRouter"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Auth --------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailBackend",  # customers: email + password
    "django.contrib.auth.backends.ModelBackend",  # admin: username + password
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

# --- I18N ----------------------------------------------------------------------
LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --- Static & media --------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Email -------------------------------------------------------------------------
# "file" (default) writes every email to sent_emails/ so the demo works offline.
EMAIL_MODE = os.getenv("EMAIL_MODE", "file").lower()
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "orders@example.com")
EMAIL_FILE_DIR = BASE_DIR / "sent_emails"
if EMAIL_MODE == "smtp":
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": os.getenv("EMAIL_HOST", "localhost"),
                "port": int(os.getenv("EMAIL_PORT", "587")),
                "username": os.getenv("EMAIL_HOST_USER", ""),
                "password": os.getenv("EMAIL_HOST_PASSWORD", ""),
                "use_tls": env_bool("EMAIL_USE_TLS", True),
            },
        },
    }
else:
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.filebased.EmailBackend",
            "OPTIONS": {"file_path": EMAIL_FILE_DIR},
        },
    }

# --- Messages → Bootstrap-friendly tags ---------------------------------------------
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {message_constants.ERROR: "danger"}

# --- Security (sensible defaults; tighten further for a real deployment) ----------------
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# --- Project settings -------------------------------------------------------------------
STORE_NAME = "Chowk"
RECOMMENDER = {
    "TOP_N_SIMILAR": 6,
    "TOP_N_PERSONAL": 8,
    "INTERACTION_WEIGHTS": {"purchase": 3.0, "cart": 2.0, "view": 1.0},
    "HALF_LIFE_DAYS": 14,
}
REPORTS_DIR = BASE_DIR / "reports"
