from django.db import models


class Office(models.Model):
    correlation_id = models.UUIDField(
        unique=True,
        verbose_name="Correlation ID",
        help_text="Unique identifier for this office",
    )
    name = models.CharField(max_length=255, verbose_name="Name", help_text="Name of the office")
    slug = models.SlugField(
        max_length=50,
        verbose_name="Slug",
        help_text="URL-friendly version of the office name",
    )
    code = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Code",
        help_text="Office code or identifier",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="When this office was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When this office was last updated",
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Office"
        verbose_name_plural = "Offices"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
