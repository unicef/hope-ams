from django.db import models


class Programme(models.Model):
    correlation_id = models.UUIDField(
        unique=True,
        verbose_name="Correlation ID",
        help_text="Unique identifier for this programme",
    )
    name = models.CharField(max_length=255, verbose_name="Name", help_text="Name of the programme")
    code = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Code",
        help_text="Programme code or identifier",
    )
    office = models.ForeignKey(
        "Office",
        on_delete=models.CASCADE,
        verbose_name="Office",
        help_text="Office this programme belongs to",
        related_name="programmes",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="When this programme was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When this programme was last updated",
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
