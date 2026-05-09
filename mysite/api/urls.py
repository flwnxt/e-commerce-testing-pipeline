"""
mysite/api/urls.py
==================
URL patterns for the 3 performance-demo APIs.

Mount in mysite/urls.py:
    path("api/", include("api.urls")),
"""

from django.urls import path

from . import views

urlpatterns = [
    # API 1 — enrolled courses + analytics (requires login)
    path("user/my-courses/", views.my_courses, name="api-my-courses"),
    path("locust-login/", views.locust_login, name="locust-login"),

    # API 2 — course search
    path("courses/search/", views.search_courses, name="api-search-courses"),

    # API 3 — popular course recommendations
    path("courses/recommendations/", views.recommendations, name="api-recommendations"),
]
