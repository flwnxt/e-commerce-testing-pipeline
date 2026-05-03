from playwright.sync_api import Page, expect


class ContactThankYouPage:
    """
    Page Object Model for the Contact form thank you page.
    Shown after a successful contact form submission.
    Corresponding template: pages/templates/pages/contact_page_landing.html
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_test_id("contact-thankyou-heading")

    def expect_visible(self) -> None:
        """Assert the thank-you heading is visible — confirms successful form submission."""
        self.page.wait_for_url("**/contact-page/**", timeout=10000)
        expect(self.heading).to_be_visible()