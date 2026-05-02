from playwright.sync_api import Page, expect


class HomePage:
    """
    Page Object Model for the Homepage (/).

    Courses are displayed directly on the homepage in a card grid.
    This is the entry point for the browse courses → course detail flow.

    Corresponding template: home/templates/home/home_page.html
    Required data-testid attributes in that template:
      - data-testid="home-course-card"        on each <article> card
      - data-testid="home-course-title-link"  on each course title <a>
    """

    URL = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

        self.course_cards = page.get_by_test_id("home-course-card")
        self.card_title_links = page.get_by_test_id("home-course-title-link")

    def navigate(self, base_url: str) -> None:
        """Navigate to the homepage."""
        self.page.goto(f"{base_url}{self.URL}")

    def get_course_count(self) -> int:
        """Return the number of course cards visible on the homepage."""
        return self.course_cards.count()

    def click_first_course(self) -> str:
        """
        Click the first course card title and return its text
        so the test can verify the destination page.
        """
        first_link = self.card_title_links.first
        title_text = first_link.inner_text()
        # Make sure the page is fully loaded
        with self.page.expect_navigation():
            first_link.click()
        return title_text