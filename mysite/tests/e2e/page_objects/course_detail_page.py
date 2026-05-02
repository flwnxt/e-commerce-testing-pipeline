from playwright.sync_api import Page, expect


class CourseDetailPage:
    """
    Page Object Model for the Course Detail page.

    Locators use data-testid attributes exclusively.

    Corresponding template: page_object/templates/page_object/course_detail_page.html
    Required data-testid attributes in that template:
      - data-testid="detail-heading"    on the <h1>
      - data-testid="detail-price"      on the price element(s)
      - data-testid="detail-breadcrumb" on the breadcrumb <div>
    """

    def __init__(self, page: Page) -> None:
        self.page = page

        # Locators — keyed to data-testid attributes in the template
        self.heading = page.get_by_test_id("detail-heading")
        self.price = page.get_by_test_id("detail-price")
        self.breadcrumb = page.get_by_test_id("detail-breadcrumb")

    def expect_heading_to_contain(self, text: str) -> None:
        """Assert the page <h1> contains the expected course title."""
        expect(self.heading).to_contain_text(text)

    def expect_price_visible(self) -> None:
        """Assert that a price element is visible on the page."""
        expect(self.price.first).to_be_visible()

    def expect_breadcrumb_visible(self) -> None:
        """Assert that the breadcrumb navigation is visible."""
        expect(self.breadcrumb).to_be_visible()