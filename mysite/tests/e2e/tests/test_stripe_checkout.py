import pytest
from playwright.sync_api import Page

from page_objects.pricing_page import PricingPage
from page_objects.stripe_page import StripePage
from page_objects.payment_pages import PaymentSuccessPage, PaymentCancelPage


# ---------------------------------------------------------------------------
# Tests: Pricing → Stripe checkout → Success / Cancel
# ---------------------------------------------------------------------------
# User stories:
#   Test 2: A visitor clicks "Buy now" on the pricing page, fills in
#           Stripe test card details, completes the payment, and lands
#           on the payment success page.
#
#   Test 3: A visitor clicks "Buy now" on the pricing page, reaches
#           the Stripe checkout, then cancels and lands on the
#           payment cancel page.
#
# What these tests verify:
#   - The pricing page has at least one Buy now button
#   - Clicking it redirects to Stripe hosted checkout
#   - Completing payment redirects back to /payment/success/
#   - Cancelling redirects back to /payment/cancel/
#
# Note: These tests use Stripe test mode only.
# Test card: 4242 4242 4242 4242
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestStripeCheckout:

    def test_successful_payment_redirects_to_success_page(
        self, page: Page, base_url: str
    ) -> None:
        """
        Full payment flow: Pricing → Stripe checkout → fill test card → Success page.
        """
        # Step 1: Navigate to pricing and click Buy now
        pricing = PricingPage(page)
        pricing.navigate(base_url)
        pricing.click_first_buy_button()

        # Step 2: Wait for Stripe checkout to load and fill contact and card details
        stripe = StripePage(page)
        stripe.wait_for_stripe()
        stripe.fill_contact_details()
        stripe.fill_card_details()
        stripe.submit()

        # Step 3: Verify we landed on the success page
        success = PaymentSuccessPage(page)
        success.wait_for_success_page()
        success.expect_visible()

    def test_cancel_payment_redirects_to_cancel_page(
        self, page: Page, base_url: str
    ) -> None:
        """
        Cancel flow: Pricing → Stripe checkout → click Back → Cancel page.
        """
        # Step 1: Navigate to pricing and click Buy now
        pricing = PricingPage(page)
        pricing.navigate(base_url)
        pricing.click_first_buy_button()

        # Step 2: Wait for Stripe to load, then cancel
        stripe = StripePage(page)
        stripe.wait_for_stripe()
        stripe.cancel()

        # Step 3: Verify we landed on the cancel page
        cancel = PaymentCancelPage(page)
        cancel.expect_visible()