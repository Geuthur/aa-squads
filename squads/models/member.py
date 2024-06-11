"""
Memberships Model
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from allianceauth.authentication.models import User

from squads.hooks import get_extension_logger
from squads.models.groups import Groups
from squads.view_helpers.core import generate_unique_id

logger = get_extension_logger(__name__)


class Memberships(models.Model):
    """Memberships Model store Membership Data."""

    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    req_filters = models.BooleanField(default=False)
    application_id = models.CharField(
        max_length=12, default=generate_unique_id, unique=True, blank=True
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} in {self.group.name}"

    class Meta:
        default_permissions = ()


class Pending(models.Model):
    """Pending Model store Groups Data."""

    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    req_filters = models.BooleanField(default=True)
    comment = models.TextField(blank=True)
    application_id = models.CharField(
        max_length=12, primary_key=True, default=generate_unique_id, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
