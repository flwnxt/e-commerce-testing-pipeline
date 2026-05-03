from playwright.sync_api import Page, expect


class PricingPage:
    """
    Page Object Model for the Pricing page.

    Locators use data-testid attributes exclusively.

    Corresponding template: pages/templates/pages/pricing_page.html
    """

    URL = "/pricing/"

    def __init__(self, page: Page) -> None:
        self.page = page

        self.buy_buttons = page.get_by_test_id("pricing-buy-button")

    def navigate(self, base_url: str) -> None:
        """Navigate to the pricing page."""
        self.page.goto(f"{base_url}{self.URL}")

    def click_first_buy_button(self) -> None:
        """Click the first available Buy now button."""
        self.buy_buttons.first.click()