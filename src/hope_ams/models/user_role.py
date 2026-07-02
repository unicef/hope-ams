from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext as _


class UserRole(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name=_("User"),
        help_text=_("The user associated with this role"),
    )
    country_office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("Office"),
        help_text=_("The office this role is associated with"),
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        verbose_name=_("Programme"),
        blank=True,
        null=True,
        help_text=_("The programme this role is associated with (if any)"),
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name=_("Group"),
        help_text=_("The group this role belongs to"),
    )
    expires = models.DateField(
        verbose_name=_("Expiration Date"),
        blank=True,
        null=True,
        help_text=_("Date when this role expires"),
    )

    class Meta:
        app_label = "hope_ams"
        constraints = [
            models.UniqueConstraint(
                name="detection_userrole_unique_role",
                fields=["user", "country_office", "group"],
            ),
        ]
        verbose_name = _("User Role")
        verbose_name_plural = _("User Roles")

    def __str__(self) -> str:
        return f"{self.user} @ {self.country_office}"
