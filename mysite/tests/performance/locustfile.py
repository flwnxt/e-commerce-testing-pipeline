"""
tests/performance/locustfile.py
================================
Performance tests for the 3 LearnHub APIs.

Each API is tested in two modes to produce before/after comparison data:
  - ?mode=slow  → intentionally broken path (N+1, full table scan, no cache)
  - (default)   → optimised path (select_related, pagination, cache)

Run locally:
  locust -f tests/performance/locustfile.py --host=http://localhost:8000

Run headless (CI / Jenkins):
  locust -f tests/performance/locustfile.py \
    --host=http://web:8000 \
    --headless -u 50 -r 10 --run-time 60s \
    --html=test-results/locust/report.html \
    --csv=test-results/locust/results
"""

import os

from locust import HttpUser, between, task


# ---------------------------------------------------------------------------
# Credentials — override via environment variables in CI
# ---------------------------------------------------------------------------
TEST_USER_NAME = os.environ.get("LOCUST_USER_EMAIL", "seed_user_0001")
TEST_USER_PASSWORD = os.environ.get("LOCUST_USER_PASSWORD", "TestPass123!")


class LearnHubUser(HttpUser):
    """
    Simulates a logged-in user hitting all 3 performance-demo APIs.

    wait_time controls think time between requests — keeps load realistic
    and prevents hammering the server without breathing room.
    between(1, 3) means each virtual user waits 1-3 seconds between tasks.
    """

    wait_time = between(1, 3)

    # -----------------------------------------------------------------------
    # Login — runs once per virtual user before tasks start
    # -----------------------------------------------------------------------

    def on_start(self):
        """
        Log in via Django's session auth before running any tasks.

        Why session auth and not a token?
        The APIs use @login_required which checks the Django session cookie.
        Locust's HttpSession automatically stores and sends cookies, so after
        a successful login POST, every subsequent request is authenticated.
        """
        # Step 1: GET the login page to retrieve the CSRF token
        response = self.client.get("/django-admin/login/")
        csrf_token = response.cookies.get("csrftoken")

        # Step 2: POST credentials with the CSRF token
        self.client.post(
            "/django-admin/login/",
            data={
                "username": TEST_USER_NAME,
                "password": TEST_USER_PASSWORD,
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": f"{self.host}/django-admin/login/"},
        )

    # -----------------------------------------------------------------------
    # API 1 — /api/user/my-courses/
    # -----------------------------------------------------------------------

    @task(2)
    def my_courses_slow(self):
        """
        SLOW: N+1 queries + 3 separate aggregate queries + bloated payload.
        task(2) = called twice as often as task(1) tasks — more data points
        for the slow path since it's the interesting comparison.
        """
        self.client.get(
            "/api/user/my-courses/?mode=slow",
            name="/api/user/my-courses/ [SLOW]",  # name groups requests in the report
        )

    @task(2)
    def my_courses_fast(self):
        """
        FAST: select_related + single aggregate + minimal payload.
        """
        self.client.get(
            "/api/user/my-courses/",
            name="/api/user/my-courses/ [FAST]",
        )

    # -----------------------------------------------------------------------
    # API 2 — /api/courses/search/
    # -----------------------------------------------------------------------

    @task(1)
    def search_courses_slow(self):
        """
        SLOW: full table scan, no pagination, returns all fields (~8 MB payload).
        """
        self.client.get(
            "/api/courses/search/?q=python&mode=slow",
            name="/api/courses/search/ [SLOW]",
        )

    @task(1)
    def search_courses_fast(self):
        """
        FAST: indexed lookup, only needed fields, paginated (~15 KB payload).
        """
        self.client.get(
            "/api/courses/search/?q=python",
            name="/api/courses/search/ [FAST]",
        )

    # -----------------------------------------------------------------------
    # API 3 — /api/courses/recommendations/
    # -----------------------------------------------------------------------

    @task(1)
    def recommendations_slow(self):
        """
        SLOW: cache disabled — every request hits the database.
        """
        self.client.get(
            "/api/courses/recommendations/?mode=slow",
            name="/api/courses/recommendations/ [SLOW]",
        )

    @task(1)
    def recommendations_fast(self):
        """
        FAST: result cached for 5 minutes — only first request hits DB.
        """
        self.client.get(
            "/api/courses/recommendations/",
            name="/api/courses/recommendations/ [FAST]",
        )