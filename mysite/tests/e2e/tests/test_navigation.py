import pytest
from playwright.sync_api import Page

from page_objects.navigation_component import NavigationComponent


# ---------------------------------------------------------------------------
# Test: Navigation → Visit all pages via nav links
# ---------------------------------------------------------------------------
# User story:
#   A visitor uses the navigation bar to reach every page on the site.
#   Each nav link must have the correct label and lead to a live page.
#
# What this test verifies:
#   1. All expected nav links are present
#   2. Each nav link has the correct label text
#   3. Clicking each link navigates to a live page (no 404)
#
# Intentional failure:
#   The "About" page has been renamed in Wagtail admin to "About is".
#   The test expects the label "About" — this mismatch causes a failure.
#   This simulates a realistic scenario where a content editor renames
#   a page in the CMS without updating the corresponding test expectation.
# ---------------------------------------------------------------------------


# Expected nav links: slug → expected label
# Update slugs to match your Wagtail page slugs
EXPECTED_NAV_LINKS = {
    "home": "Home",
    "pricing": "Pricing",
    "about-page": "About Us",          # ← intentional failure: admin shows "About is"
    "contact-page": "Contact page",
    "faq-page": "FAQ Page",
}


@pytest.mark.e2e
class TestNavigation:

    def test_all_nav_links_have_correct_labels(self, page: Page, base_url: str) -> None:
        """
        Every nav link must display the correct label text.

        This test intentionally fails on the About Us page — its label
        was changed in Wagtail admin from 'About Us' to 'About is',
        demonstrating how a CMS content change can break a test expectation.
        """
        nav = NavigationComponent(page)
        nav.navigate(base_url)

        for slug, expected_text in EXPECTED_NAV_LINKS.items():
            nav.expect_link_text(slug, expected_text)

    def test_all_nav_links_lead_to_live_pages(self, page: Page, base_url: str) -> None:
        """
        Clicking each nav link must navigate to a live page — no 404s.
        """
        nav = NavigationComponent(page)

        for slug in EXPECTED_NAV_LINKS:
            nav.navigate(base_url)
            nav.click_link(slug)
            # Verify the page loaded successfully — no 404 or 500
            expect_no_error = page.locator("h1")
            assert expect_no_error.count() > 0, (
                f"Nav link '{slug}' led to a page with no <h1> — possible 404 or error page."
            )