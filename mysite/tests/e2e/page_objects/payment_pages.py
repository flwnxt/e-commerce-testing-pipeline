from playwright.sync_api import Page, expect


class PaymentSuccessPage:
    """
    Page Object Model for the Payment Success page.

    Corresponding template: pages/templates/pages/payment_success.html
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_test_id("payment-success-heading")

    def wait_for_success_page(self) -> None:
        """Assert the success heading is visible"""
        self.page.wait_for_url("**/payment/success/**", timeout=30000)

    def expect_visible(self) -> None:
        """Assert the success heading is visible — confirms successful payment redirect."""
        expect(self.heading).to_be_visible()


class PaymentCancelPage:
    """
    Page Object Model for the Payment Cancel page.

    Corresponding template: pages/templates/pages/payment_cancel.html
    Required data-testid attributes:
      - data-testid="payment-cancel-heading"  on the <h1>
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_test_id("payment-cancel-heading")

    def expect_visible(self) -> None:
        """Assert the cancel heading is visible — confirms cancel redirect."""
        expect(self.heading).to_be_visible()