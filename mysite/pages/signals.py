"""
mysite/pages/signals.py
========================
Invalidates the recommendations cache whenever a new Enrollment is created.
This keeps /api/courses/recommendations/ fresh without waiting for the 5-min TTL.

Wire up in pages/apps.py — see comment below.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


def register():
    """Called from PagesConfig.ready() to connect signals."""
    from pages.models import Enrollment  # noqa: import inside function avoids circular import
    from api.views import invalidate_recommendations_cache

    @receiver(post_save, sender=Enrollment)
    def on_enrollment_saved(sender, instance, created, **kwargs):
        if created:
            invalidate_recommendations_cache()
