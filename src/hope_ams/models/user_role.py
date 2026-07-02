from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models


class UserRole(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name="User",
        help_text="The user associated with this role",
    )
    country_office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Office",
        help_text="The office this role is associated with",
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Programme",
        help_text="The programme this role is associated with (if any)",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name="Group",
        help_text="The group this role belongs to",
    )
    expires = models.DateField(
        null=True,
        blank=True,
        verbose_name="Expiration Date",
        help_text="Date when this role expires",
    )

    class Meta:
        app_label = "hope_ams"
        constraints = [
            models.UniqueConstraint(
                name="detection_userrole_unique_role",
                fields=["user", "country_office", "group"],
            ),
        ]
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"

    def __str__(self) -> str:
        return f"{self.user} @ {self.country_office}"
