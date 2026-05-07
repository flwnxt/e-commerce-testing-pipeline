"""
mysite/api/views.py
===================
3 API endpoints for performance thesis demonstration.

Each endpoint supports ?mode=slow to switch between the intentionally
broken (slow) implementation and the optimised (fast) implementation.

Endpoints:
  GET /api/user/my-courses/          → requires login (session auth)
  GET /api/courses/search/?q=...     → public
  GET /api/courses/recommendations/  → public
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from pages.models import CourseDetailPage, Enrollment

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _is_slow(request):
    """Return True when the caller explicitly opts into the slow code path."""
    return request.GET.get("mode") == "slow"


# ─────────────────────────────────────────────────────────────────────────────
# API 1 — /api/user/my-courses/
# ─────────────────────────────────────────────────────────────────────────────

@require_GET
@login_required
def my_courses(request):
    """
    Returns the authenticated user's enrolled courses + analytics summary.

    SLOW path  (?mode=slow):
      - Fetches enrollments without select_related  → N+1 queries
        (1 query for enrollments + 1 per course to get title/instructor/price)
      - Runs 3 separate aggregate queries (COUNT, SUM, MAX)
      - Serialises every field on every course → ~500 KB payload

    FAST path  (default):
      - select_related('course') → 1 query for enrollments + courses joined
      - Single aggregate() call  → 1 query for all 3 stats
      - Only serialises needed fields → ~12 KB payload
    """
    if _is_slow(request):
        return _my_courses_slow(request)
    return _my_courses_fast(request)


def _my_courses_slow(request):
    """
    ❌ SLOW — N+1 queries + 3 separate aggregate queries + bloated payload.

    Demonstrates:
      - N+1: fetching course.title triggers a separate DB hit per enrollment
      - Over-fetching: returns all model fields including unused ones
      - Multiple aggregates: 3 queries instead of 1
    """
    # Query 1: get enrollments (no prefetch — each .course access below = new query)
    enrollments = list(Enrollment.objects.filter(user=request.user))

    courses = []
    for enrollment in enrollments:
        # ← N+1: each access hits the DB again
        course = enrollment.course
        courses.append({
            "id": course.id,
            "title": course.title,
            "slug": course.slug,
            "instructor": course.instructor,
            "price": str(course.price),
            "description": str(course.description),        # RichTextField — large HTML blob
            "course_content": str(course.course_content),  # StreamField — very large
            "enrolled_at": enrollment.enrolled_at.isoformat(),
            "amount_paid": str(enrollment.amount_paid),
        })

    # 3 separate aggregate queries
    user_enrollments = Enrollment.objects.filter(user=request.user)
    count = user_enrollments.count()                           # Query N+2
    total_spent = user_enrollments.aggregate(s=Sum("amount_paid"))["s"] or 0  # Query N+3
    last_enrolled = user_enrollments.aggregate(m=Max("enrolled_at"))["m"]     # Query N+4

    return JsonResponse({
        "mode": "slow",
        "analytics": {
            "total_courses": count,
            "total_spent": str(total_spent),
            "last_enrolled_at": last_enrolled.isoformat() if last_enrolled else None,
        },
        "courses": courses,
    })


def _my_courses_fast(request):
    """
    ✅ FAST — select_related + single aggregate + minimal payload.

    Demonstrates:
      - select_related('course'): 1 SQL JOIN → 1 query total
      - aggregate() with multiple annotations → 1 query for all stats
      - Only returns fields the client actually needs
    """
    # 1 query: JOIN enrollments + wagtail page + coursedetailpage
    enrollments = (
        Enrollment.objects
        .filter(user=request.user)
        .select_related("course")
    )

    # 1 aggregate query for all 3 stats
    stats = enrollments.aggregate(
        total_courses=Count("id"),
        total_spent=Sum("amount_paid"),
        last_enrolled_at=Max("enrolled_at"),
    )

    courses = [
        {
            "id": e.course.id,
            "title": e.course.title,
            "instructor": e.course.instructor,
            "price": str(e.course.price),
            "enrolled_at": e.enrolled_at.isoformat(),
            "amount_paid": str(e.amount_paid),
        }
        for e in enrollments
    ]

    return JsonResponse({
        "mode": "fast",
        "analytics": {
            "total_courses": stats["total_courses"] or 0,
            "total_spent": str(stats["total_spent"] or 0),
            "last_enrolled_at": (
                stats["last_enrolled_at"].isoformat()
                if stats["last_enrolled_at"] else None
            ),
        },
        "courses": courses,
    })


# ─────────────────────────────────────────────────────────────────────────────
# API 2 — /api/courses/search/
# ─────────────────────────────────────────────────────────────────────────────

@require_GET
def search_courses(request):
    """
    Search courses by title or instructor name.

    Query params:
      q        — search term (required)
      mode     — "slow" for intentionally broken path
      page     — page number (fast path only, default 1)
      per_page — results per page (fast path only, default 20)

    SLOW path (?mode=slow):
      - icontains on non-indexed CharField → full table scan on every request
      - Returns ALL matching courses with ALL fields → ~8 MB payload
      - No pagination

    FAST path (default):
      - Same icontains but with DB index on title (added in migration)
      - Returns only needed fields
      - Paginated (default 20 per page) → ~15-20 KB payload
    """
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"error": "Missing required parameter: q"}, status=400)

    if _is_slow(request):
        return _search_courses_slow(q)
    return _search_courses_fast(request, q)


def _search_courses_slow(q):
    """
    ❌ SLOW — no index, no pagination, bloated payload.

    Demonstrates:
      - Full table scan on unindexed column
      - Returns all fields including StreamField (course_content) — can be MBs per record
      - Entire result set in one response → payload grows linearly with DB size
    """
    courses = CourseDetailPage.objects.live().filter(
        title__icontains=q
    )

    results = []
    for course in courses:
        results.append({
            "id": course.id,
            "title": course.title,
            "slug": course.slug,
            "instructor": course.instructor,
            "price": str(course.price),
            "description": str(course.description),        # Large HTML blob
            "course_content": str(course.course_content),  # Very large StreamField blob
        })

    return JsonResponse({
        "mode": "slow",
        "count": len(results),
        "results": results,
    })


def _search_courses_fast(request, q):
    """
    ✅ FAST — indexed lookup, minimal fields, paginated.

    Demonstrates:
      - only() to fetch exactly the columns needed → avoids loading StreamField
      - Pagination keeps payload constant regardless of DB size
      - Predictable memory use under load
    """
    page_num = int(request.GET.get("page", 1))
    per_page = min(int(request.GET.get("per_page", 20)), 100)  # cap at 100

    qs = (
        CourseDetailPage.objects.live()
        .filter(title__icontains=q)
        .only("id", "title", "slug", "instructor", "price")
        .order_by("title")
    )

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_num)

    results = [
        {
            "id": course.id,
            "title": course.title,
            "slug": course.slug,
            "instructor": course.instructor,
            "price": str(course.price),
        }
        for course in page_obj
    ]

    return JsonResponse({
        "mode": "fast",
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "page": page_num,
        "per_page": per_page,
        "results": results,
    })


# ─────────────────────────────────────────────────────────────────────────────
# API 3 — /api/courses/recommendations/
# ─────────────────────────────────────────────────────────────────────────────

RECOMMENDATIONS_CACHE_KEY = "api:recommendations:popular"
RECOMMENDATIONS_CACHE_TTL = 60 * 5  # 5 minutes


@require_GET
def recommendations(request):
    """
    Returns popular courses sorted by enrollment count.

    SLOW path (?mode=slow):
      - Cache disabled — every request hits the DB
      - Demonstrates DB overload under concurrent Locust load

    FAST path (default):
      - Results cached for 5 minutes
      - Cache is invalidated when a new enrollment is created
        (call invalidate_recommendations_cache() from the enrollment signal)
      - First request after cold start/invalidation hits DB; subsequent ones
        are served from cache → Locust shows the latency drop clearly
    """
    if _is_slow(request):
        return _recommendations_slow()
    return _recommendations_fast()


def _recommendations_slow():
    """
    ❌ SLOW — no cache, hits DB on every request.

    Demonstrates:
      - DB query on every concurrent request
      - Response time degrades linearly with user count (Locust shows this)
    """
    courses = (
        CourseDetailPage.objects.live()
        .annotate(enrollment_count=Count("enrollments"))
        .order_by("-enrollment_count")
        .only("id", "title", "slug", "instructor", "price")[:20]
    )

    results = [
        {
            "id": c.id,
            "title": c.title,
            "slug": c.slug,
            "instructor": c.instructor,
            "price": str(c.price),
            "enrollment_count": c.enrollment_count,
        }
        for c in courses
    ]

    return JsonResponse({
        "mode": "slow",
        "cached": False,
        "results": results,
    })


def _recommendations_fast():
    """
    ✅ FAST — 5-minute cache, DB only on cold start or after invalidation.

    Demonstrates:
      - Cache hit: ~1ms (no DB)
      - Cache miss: DB query, then cached for 5 min
      - Locust shows the latency cliff between first request and subsequent ones
    """
    cached = cache.get(RECOMMENDATIONS_CACHE_KEY)
    if cached is not None:
        return JsonResponse({
            "mode": "fast",
            "cached": True,
            "results": cached,
        })

    # Cache miss — query the DB
    courses = (
        CourseDetailPage.objects.live()
        .annotate(enrollment_count=Count("enrollments"))
        .order_by("-enrollment_count")
        .only("id", "title", "slug", "instructor", "price")[:20]
    )

    results = [
        {
            "id": c.id,
            "title": c.title,
            "slug": c.slug,
            "instructor": c.instructor,
            "price": str(c.price),
            "enrollment_count": c.enrollment_count,
        }
        for c in courses
    ]

    cache.set(RECOMMENDATIONS_CACHE_KEY, results, RECOMMENDATIONS_CACHE_TTL)

    return JsonResponse({
        "mode": "fast",
        "cached": False,
        "results": results,
    })


def invalidate_recommendations_cache():
    """
    Call this whenever a new Enrollment is saved to keep recommendations fresh.

    Usage in a Django signal (pages/signals.py):

        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from pages.models import Enrollment
        from api.views import invalidate_recommendations_cache

        @receiver(post_save, sender=Enrollment)
        def on_enrollment_saved(sender, instance, created, **kwargs):
            if created:
                invalidate_recommendations_cache()
    """
    cache.delete(RECOMMENDATIONS_CACHE_KEY)
