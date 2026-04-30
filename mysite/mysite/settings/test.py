# mysite/settings/test.py
# =============================================================================
# Test environment settings — used by the CI/CD pipeline.
# =============================================================================
# Inherits from base.py directly
# =============================================================================

from .base import *  # noqa: F401, F403

# =============================================================================
# GENERAL
# =============================================================================

DEBUG = True
SECRET_KEY = "django-test-secret-key-only-for-ci-pipeline"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "django.contrib.postgres",
]

# =============================================================================
# DATABASE — PostgreSQL for test environment
# =============================================================================
# Connection details match the 'db' service in docker-compose.test.yml.
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "learnhub_test",
        "USER": "learnhub",
        "PASSWORD": "learnhub_test_pw",
        "HOST": "db",  # Docker Compose service name
        "PORT": "5432",
    }
}

# =============================================================================
# EMAIL — Console backend (no real emails sent during tests)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# CACHING — Local memory cache for test isolation
# =============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}