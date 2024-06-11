"""
Groups Model
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from allianceauth.authentication.models import User

from squads.hooks import get_extension_logger
from squads.managers import GroupsManager

logger = get_extension_logger(__name__)


class Groups(models.Model):
    """Groups Model store Groups Data."""

    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="group_owner"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    req_approve = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="squads/groups_images/", blank=True, null=True)

    objects = GroupsManager()

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        default_permissions = ()
