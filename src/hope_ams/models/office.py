from django.db import models
from django.utils.translation import gettext as _


class Office(models.Model):
    correlation_id = models.UUIDField(
        verbose_name=_("Correlation ID"),
        unique=True,
        help_text=_("Unique identifier for this office"),
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("Name of the office"),
    )
    slug = models.SlugField(
        verbose_name=_("Slug"),
        max_length=50,
        help_text=_("URL-friendly version of the office name"),
    )
    code = models.CharField(
        verbose_name=_("Code"),
        max_length=100,
        blank=True,
        default="",
        help_text=_("Office code or identifier"),
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        help_text=_("When this office was created"),
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        auto_now=True,
        help_text=_("When this office was last updated"),
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = _("Office")
        verbose_name_plural = _("Offices")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
