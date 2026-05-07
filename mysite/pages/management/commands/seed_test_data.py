"""
mysite/pages/management/commands/seed_test_data.py
===================================================
Creates [SEED]-prefixed test courses AND enrollments so all 3 APIs have data.

Usage:
  python manage.py seed_test_data --count=500
  python manage.py seed_test_data --count=500 --clear    # wipe existing seed data first
  python manage.py seed_test_data --clear                # wipe only, no new seeds
"""

import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Page

from pages.models import CourseDetailPage, CourseCatalogPage, Enrollment

User = get_user_model()

SEED_PREFIX = "[SEED]"

INSTRUCTORS = [
    "Ana Popescu", "Mihai Ionescu", "Elena Dumitrescu",
    "Andrei Constantin", "Maria Georgescu", "Bogdan Popa",
    "Ioana Moldovan", "Radu Stanescu", "Cristina Ilie", "Vlad Munteanu",
]

TOPICS = [
    "Python", "Django", "React", "Docker", "PostgreSQL",
    "Machine Learning", "DevOps", "Testing", "JavaScript", "FastAPI",
    "Kubernetes", "Redis", "GraphQL", "REST APIs", "AWS",
    "Security", "Git", "Linux", "TypeScript", "Data Engineering",
]

LEVELS = ["Beginner", "Intermediate", "Advanced"]


class Command(BaseCommand):
    help = "Seed [SEED]-prefixed test courses and enrollments for performance testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of courses to create (default: 100)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all [SEED]-prefixed data before creating new data",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Number of test users to create/reuse (default: 10)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_seed_data()

        if options.get("count", 0) == 0:
            self.stdout.write(self.style.SUCCESS("Cleared. Nothing to seed."))
            return

        catalog_page = self._get_or_create_catalog()
        users = self._get_or_create_users(options["users"])
        courses = self._create_courses(options["count"], catalog_page)
        self._create_enrollments(courses, users)

        self.stdout.write(self.style.SUCCESS(
            f"✅  Seeded {len(courses)} courses and enrollments for {len(users)} users."
        ))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _clear_seed_data(self):
        # Enrollments are deleted via CASCADE when courses are deleted
        deleted_courses, _ = (
            CourseDetailPage.objects
            .filter(title__startswith=SEED_PREFIX)
            .delete()
        )
        deleted_users, _ = (
            User.objects
            .filter(email__startswith="seed_user_")
            .delete()
        )
        self.stdout.write(f"🗑  Cleared {deleted_courses} seeded courses, {deleted_users} seeded users.")

    def _get_or_create_catalog(self):
        catalog = CourseCatalogPage.objects.filter(
            title__startswith=SEED_PREFIX
        ).first()

        if not catalog:
            root = Page.objects.filter(depth=2).first()
            if root is None:
                root = Page.objects.get(depth=1)

            catalog = CourseCatalogPage(
                title=f"{SEED_PREFIX} Test Catalog",
                slug="seed-test-catalog",
                introduction="Auto-generated catalog for performance tests.",
            )
            root.add_child(instance=catalog)
            self.stdout.write(f"Created catalog: {catalog.title}")

        return catalog

    def _get_or_create_users(self, count):
        users = []
        for i in range(1, count + 1):
            email = f"seed_user_{i:04d}@test.local"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"seed_user_{i:04d}",
                    "is_active": True,
                },
            )
            if created:
                user.set_password("TestPass123!")
                user.save()
            users.append(user)
        self.stdout.write(f"Ready: {len(users)} test users.")
        return users

    def _create_courses(self, count, catalog_page):
        courses = []
        existing_slugs = set(
            CourseDetailPage.objects
            .filter(title__startswith=SEED_PREFIX)
            .values_list("slug", flat=True)
        )

        for i in range(1, count + 1):
            topic = random.choice(TOPICS)
            level = random.choice(LEVELS)
            instructor = random.choice(INSTRUCTORS)
            title = f"{SEED_PREFIX} {topic} for {level}s — #{i:04d}"
            base_slug = slugify(f"seed-{topic}-{level}-{i:04d}")

            # Ensure uniqueness
            slug = base_slug
            suffix = 1
            while slug in existing_slugs:
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            existing_slugs.add(slug)

            price = Decimal(random.choice([
                "9.99", "14.99", "19.99", "24.99", "29.99",
                "39.99", "49.99", "59.99", "79.99", "99.99",
            ]))

            course = CourseDetailPage(
                title=title,
                slug=slug,
                description=f"<p>Learn {topic} at {level} level with {instructor}.</p>",
                price=price,
                instructor=instructor,
                live=True,
            )
            catalog_page.add_child(instance=course)
            courses.append(course)

        self.stdout.write(f"Created {len(courses)} seeded courses.")
        return courses

    def _create_enrollments(self, courses, users):
        """
        Each user enrolls in a random subset of courses (20–60% of catalog).
        Skips duplicates silently (unique_together constraint).
        """
        created = 0
        for user in users:
            sample_size = random.randint(
                max(1, len(courses) // 5),
                max(1, len(courses) // 2),
            )
            enrolled_courses = random.sample(courses, min(sample_size, len(courses)))
            for course in enrolled_courses:
                _, was_created = Enrollment.objects.get_or_create(
                    user=user,
                    course=course,
                    defaults={"amount_paid": course.price},
                )
                if was_created:
                    created += 1

        self.stdout.write(f"Created {created} enrollments.")
