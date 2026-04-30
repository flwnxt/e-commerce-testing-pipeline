# tests/conftest.py
# =============================================================================
# Pytest + Playwright configuration
# =============================================================================
# This file is automatically loaded by pytest before any tests run.
# It configures Playwright's browser settings and provides shared fixtures
# that all test files can use.
#
# In Playwright for Python, configuration lives here (conftest.py)
# pytest-playwright reads these fixtures to know which browser to launch and how to configure it.
# =============================================================================

import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """
    Browser launch arguments — applied once per test session.
    Headless mode is used in CI (no display available).
    """
    return {
        "headless": True,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Browser context arguments — applied to every new browser context.
    Sets viewport size and other browser-level settings.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


# =============================================================================
# pytest configuration
# =============================================================================

def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "enrollment: Enrollment flow tests")
    config.addinivalue_line("markers", "search: Search functionality tests")
    config.addinivalue_line("markers", "dashboard: Dashboard tests")