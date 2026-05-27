import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "niceid.apps.NiceIDConfig",
    "testproj.testapp",
]

MIDDLEWARE = []
ROOT_URLCONF = "testproj.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

if os.environ.get("POSTGRES_HOST"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "niceid"),
        "USER": os.environ.get("POSTGRES_USER", "niceid"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "niceid"),
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
