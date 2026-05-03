import pytest
from playwright.sync_api import Page

from page_objects.faq_page import FAQPage


# ---------------------------------------------------------------------------
# Test: FAQ page → Click questions → Accordion opens/closes
# ---------------------------------------------------------------------------
# User story:
#   A visitor opens the FAQ page, clicks a question, and the answer
#   expands. Clicking another question opens it and closes the previous.
#   Clicking the same open question closes it.
#
# What this test verifies:
#   1. The FAQ page loads with at least one question
#   2. Clicking a closed question opens it
#   3. Clicking a second question opens it and closes the first
#   4. Clicking an open question closes it
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestFAQAccordion:

    def test_faq_page_has_questions(self, page: Page, base_url: str) -> None:
        """
        The FAQ page must have at least one question.
        Precondition for the accordion interaction tests.
        """
        faq = FAQPage(page)
        faq.navigate(base_url)

        count = faq.get_item_count()
        assert count > 0, (
            f"Expected at least 1 FAQ item, found {count}. "
            "Make sure FAQ items are added in Wagtail admin."
        )

    def test_clicking_question_opens_answer(self, page: Page, base_url: str) -> None:
        """
        Clicking a closed question opens its answer.
        """
        faq = FAQPage(page)
        faq.navigate(base_url)

        # First question should be closed initially
        assert not faq.is_answer_open(0), "Expected first FAQ item to be closed initially."

        faq.click_question(0)

        assert faq.is_answer_open(0), "Expected first FAQ item to be open after clicking."

    def test_clicking_second_question_closes_first(self, page: Page, base_url: str) -> None:
        """
        Clicking a second question opens it and closes the previously open one.
        The accordion only allows one open item at a time.
        """
        faq = FAQPage(page)
        faq.navigate(base_url)

        # Need at least 2 questions for this test
        if faq.get_item_count() < 2:
            pytest.skip("Need at least 2 FAQ items for this test.")

        # Open the first question
        faq.click_question(0)
        assert faq.is_answer_open(0), "Expected first FAQ item to be open."

        # Click the second question
        faq.click_question(1)

        # Second should now be open, first should be closed
        assert faq.is_answer_open(1), "Expected second FAQ item to be open."
        assert not faq.is_answer_open(0), "Expected first FAQ item to be closed after opening second."

    def test_clicking_open_question_closes_it(self, page: Page, base_url: str) -> None:
        """
        Clicking an already open question closes it.
        """
        faq = FAQPage(page)
        faq.navigate(base_url)

        # Open the first question
        faq.click_question(0)
        assert faq.is_answer_open(0), "Expected first FAQ item to be open."

        # Click it again to close
        faq.click_question(0)
        assert not faq.is_answer_open(0), "Expected first FAQ item to be closed after clicking again."