from playwright.sync_api import Page, expect


class ContactPage:
    """
    Page Object Model for the Contact page.

    Locators use form labels.

    Corresponding template: pages/templates/pages/contact_page.html
    """

    URL = "/contact-page/"

    def __init__(self, page: Page) -> None:
        self.page = page

        self.form = page.get_by_test_id("contact-form")
        self.submit_button = page.get_by_test_id("contact-submit-button")

    def navigate(self, base_url: str) -> None:

        """Navigate to the contact page."""
        self.page.goto(f"{base_url}{self.URL}")

    def fill_field(self, label: str, value: str) -> None:
        """Fill a form field by its label text."""

        self.form.get_by_label(label).fill(value)

    def submit(self) -> None:
        """Click the submit button."""

        self.submit_button.click()