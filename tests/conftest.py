"""Shared pytest setup. Browser fixtures are added in Phase 10."""

import pytest


@pytest.fixture(autouse=True)
def fast_password_hashing(settings):
    """Hash test passwords with a fast hasher (real hashing stays on in the app)."""
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
