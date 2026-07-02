from django.db import models
from django.utils.translation import gettext as _

from .office import Office


class Programme(models.Model):
    correlation_id = models.UUIDField(
        verbose_name=_("Correlation ID"),
        unique=True,
        help_text=_("Unique identifier for this programme"),
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("Name of the programme"),
    )
    code = models.CharField(
        verbose_name=_("Code"),
        max_length=100,
        blank=True,
        default="",
        help_text=_("Programme code or identifier"),
    )
    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        related_name="programmes",
        verbose_name=_("Office"),
        help_text=_("Office this programme belongs to"),
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        help_text=_("When this programme was created"),
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        auto_now=True,
        help_text=_("When this programme was last updated"),
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = _("Programme")
        verbose_name_plural = _("Programmes")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
