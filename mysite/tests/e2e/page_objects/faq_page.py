from playwright.sync_api import Page, expect


class FAQPage:
    """
    Page Object Model for the FAQ page.

    Locators use data-testid attributes exclusively.

    Corresponding template: pages/templates/pages/faq_page.html
    """

    URL = "/faq-page/"

    def __init__(self, page: Page) -> None:
        self.page = page

        self.faq_items = page.get_by_test_id("faq-item")
        self.question_buttons = page.get_by_test_id("faq-question-button")
        self.answers = page.get_by_test_id("faq-answer")

    def navigate(self, base_url: str) -> None:
        """Navigate to the FAQ page."""
        self.page.goto(f"{base_url}{self.URL}")

    def get_item_count(self) -> int:
        """Return the number of FAQ items on the page."""
        return self.faq_items.count()

    def click_question(self, index: int) -> None:
        """Click a question button by its index (0-based)."""
        self.question_buttons.nth(index).click()

    def is_answer_open(self, index: int) -> bool:
        """
        Check if a FAQ answer is open by inspecting the parent item's
        'open' CSS class — added by the accordion JavaScript in base.html.
        """
        item = self.faq_items.nth(index)
        classes = (item.get_attribute("class") or "").split()

        return "open" in classes