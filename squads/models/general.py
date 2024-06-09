"""
General Model
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from squads.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class General(models.Model):
    """A model defining commonly used properties and methods for Squads."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app, Squads."),
            ("squad_manager", "Can Create / Manage Squads."),
            ("squad_admin", "Can View All Squads."),
        )
