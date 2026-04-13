from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class HomePage(Page):
    hero_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Main heading displayed in the hero section"
    )
    hero_subtitle = RichTextField(
        blank=True,
        help_text="Short description below the hero title"
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Background image for the hero section"
    )

    content_panels = Page.content_panels + [
        FieldPanel("hero_title"),
        FieldPanel("hero_subtitle"),
        FieldPanel("hero_image"),
    ]