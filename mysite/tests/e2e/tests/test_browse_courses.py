import pytest
from playwright.sync_api import Page

from page_objects.home_page import HomePage
from page_objects.course_detail_page import CourseDetailPage


# ---------------------------------------------------------------------------
# Test: Browse courses → View course detail
# ---------------------------------------------------------------------------
# User story:
#   A visitor opens the homepage, sees course cards listed directly,
#   clicks the first one, and lands on the correct course detail page.
#
# What this test verifies:
#   1. The homepage displays at least one course card
#   2. Clicking a course navigates to its detail page
#   3. The detail page heading matches the course that was clicked
#   4. The detail page shows a price and a breadcrumb
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestBrowseCourses:

    def test_homepage_shows_courses(self, page: Page, base_url: str) -> None:
        """
        The homepage must display at least one course card.
        Precondition for the full browse flow.
        """
        home = HomePage(page)
        home.navigate(base_url)

        course_count = home.get_course_count()
        assert course_count > 0, (
            f"Expected at least 1 course card on the homepage, found {course_count}. "
            "Make sure published catalog page_object with courses exist in Wagtail."
        )

    def test_click_course_navigates_to_detail(self, page: Page, base_url: str) -> None:
        """
        Clicking a course card on the homepage navigates to the correct detail page.
        """
        home = HomePage(page)
        home.navigate(base_url)

        clicked_title = home.click_first_course()

        detail = CourseDetailPage(page)
        detail.expect_heading_to_contain(clicked_title)
        detail.expect_price_visible()
        detail.expect_breadcrumb_visible()