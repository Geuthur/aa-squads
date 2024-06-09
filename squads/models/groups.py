"""
Groups Model
"""

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from allianceauth.authentication.models import User

from squads.hooks import get_extension_logger
from squads.managers import GroupsManager
from squads.view_helpers.core import generate_unique_id

logger = get_extension_logger(__name__)


class Groups(models.Model):
    """Groups Model store Groups Data."""

    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="group_owner"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    require_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="squads/groups_images/", blank=True, null=True)

    objects = GroupsManager()

    def __str__(self) -> str:
        return str(self.name)

    def safe_description(self):
        return mark_safe(self.description)

    class Meta:
        default_permissions = ()


class Pending(models.Model):
    """Pending Model store Groups Data."""

    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    application = models.TextField(blank=True)
    application_id = models.CharField(
        max_length=12, primary_key=True, default=generate_unique_id, editable=False
    )

    class Meta:
        default_permissions = ()
