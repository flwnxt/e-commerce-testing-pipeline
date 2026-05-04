from playwright.sync_api import Page, expect


class NavigationComponent:
    """
    Page Object Model for the site navigation.

    The nav is part of base.html and present on every page.
    We navigate to the homepage first to access it.

    Corresponding template: mysite/templates/base.html
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.nav_links = page.get_by_test_id("nav-links")

    def navigate(self, base_url: str) -> None:
        """Navigate to the homepage to access the nav."""
        self.page.goto(base_url)

    def get_link_by_slug(self, slug: str):
        """Return a locator for a nav link by its slug-based testid."""
        return self.page.get_by_test_id(f"nav-link-{slug}")

    def expect_link_text(self, slug: str, expected_text: str) -> None:
        """Assert a nav link has the expected visible text."""
        expect(self.get_link_by_slug(slug)).to_have_text(expected_text)

    def click_link(self, slug: str) -> None:
        """Click a nav link by its slug."""
        self.get_link_by_slug(slug).click()