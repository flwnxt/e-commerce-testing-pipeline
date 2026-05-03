from playwright.sync_api import Page, expect


class StripePage:
    """
    Page Object Model for the Stripe hosted checkout page.

    Stripe renders its own checkout UI at checkout.stripe.com.
    We interact with it using stable Stripe-provided field labels.

    Note: This uses Stripe test mode credentials only.
    Test card: 4242 4242 4242 4242 (always succeeds)
    """

    # Stripe test card details
    TEST_EMAIL = "test@example.com"
    TEST_CARD_NUMBER = "4242424242424242"
    TEST_CARD_EXPIRY = "12/30"
    TEST_CARD_CVC = "123"
    TEST_CARD_NAME = "Test User"
    TEST_BILLING_POSTCODE = "12345"

    def __init__(self, page: Page) -> None:
        self.page = page

        # Contact information
        self.email_field = page.get_by_placeholder("email@example.com")
        # Card details
        self.card_number = page.get_by_placeholder("1234 1234 1234 1234")
        self.card_expiry = page.get_by_placeholder("MM / YY")
        self.card_cvc = page.get_by_placeholder("CVC")
        self.card_holder_name = page.get_by_placeholder("Full name on card")
        self.postcode_field = page.get_by_placeholder("ZIP")

    def wait_for_stripe(self) -> None:
        """Wait until the Stripe checkout page has fully loaded."""
        self.page.wait_for_url("**/checkout.stripe.com/**", timeout=15000)
        expect(self.card_number).to_be_visible(timeout=15000)

    def fill_contact_details(self) -> None:
        """Fill in the contact details on the Stripe checkout form."""

        self.email_field.fill(self.TEST_EMAIL)

    def fill_card_details(self) -> None:
        """Fill in the test card details on the Stripe checkout form."""

        # Card number
        self.card_number.fill(self.TEST_CARD_NUMBER)

        # Expiry date
        self.card_expiry.fill(self.TEST_CARD_EXPIRY)

        # CVC
        self.card_cvc.fill(self.TEST_CARD_CVC)

        # Cardholder name (not always present depending on Stripe config)
        self.card_holder_name.fill(self.TEST_CARD_NAME)

        # Billing postcode (not always present depending on Stripe config)
        if self.postcode_field.count() > 0:
            self.postcode_field.fill(self.TEST_BILLING_POSTCODE)

    def submit(self) -> None:
        """Click the pay/subscribe button to complete the checkout."""
        # Stripe uses different button labels depending on payment mode
        # 'Subscribe' for recurring, 'Pay' for one-time
        submit_button = self.page.get_by_role("button", name="Subscribe")
        if submit_button.count() == 0:
            submit_button = self.page.get_by_role("button", name="Pay")
        submit_button.click()

    def cancel(self) -> None:
        """Click the back arrow / cancel link to return to the app."""
        self.page.get_by_role("link", name="Back").click()