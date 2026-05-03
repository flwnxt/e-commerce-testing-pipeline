import pytest
from playwright.sync_api import Page

from page_objects.contact_page import ContactPage
from page_objects.contact_thank_you_page import ContactThankYouPage


# ---------------------------------------------------------------------------
# Test: Contact → Fill form → Submit → Thank you page
# ---------------------------------------------------------------------------
# User story:
#   A visitor opens the contact page, fills in the form fields,
#   submits the form, and lands on the thank-you page.
#
# What this test verifies:
#   1. The contact page loads and displays the form
#   2. The form fields can be filled
#   3. Submitting the form navigates to the thank-you page
#   4. The thank-you heading is visible
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestContactForm:

    def test_contact_form_submission(self, page: Page, base_url: str) -> None:
        """
        Fill and submit the contact form, verify the thank-you page is shown.
        """
        contact = ContactPage(page)
        contact.navigate(base_url)

        # Fill each form field by its label
        contact.fill_field("Name", "Test User")
        contact.fill_field("Email", "test@example.com")
        contact.fill_field("Message", "This is an automated test message.")

        contact.submit()

        thank_you = ContactThankYouPage(page)
        thank_you.expect_visible()