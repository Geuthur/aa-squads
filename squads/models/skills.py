"""
Memberships Model
"""

from memberaudit.models import CharacterSkillSetCheck, SkillSet

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from squads.hooks import get_extension_logger
from squads.models.groups import Groups

logger = get_extension_logger(__name__)


class BaseFilter(models.Model):
    """BaseFilter Model store BaseFilter Data."""

    description = models.CharField(
        max_length=500,
        help_text=_("Filter description shown to Users."),
    )

    def __str__(self) -> str:
        return str(self.description)

    class Meta:
        abstract = True


class SkillSetFilter(BaseFilter):
    """SkillSetFilter Model store SkillSetFilter Data."""

    skill_sets = models.ManyToManyField(
        SkillSet,
        help_text=_(
            "Users must possess the selected skill sets with at least <strong>one</strong> character."
        ),
        related_name="squads_skill_sets",
    )

    def check_skill(self, user: User):
        """Check if user Characters has required skills."""
        qs = CharacterSkillSetCheck.objects.filter(
            character__eve_character__character_ownership__user=user,
            skill_set__in=list(self.skill_sets.all()),
            failed_required_skills__isnull=True,
        )
        return qs.exists()


class GroupSkillFilter(models.Model):
    """GroupFilter Model store Filter Data."""

    group = models.OneToOneField(Groups, on_delete=models.CASCADE)
    description = models.CharField(max_length=500, default="", blank=True)
    skill_filters = models.ManyToManyField(SkillSetFilter)
    enabled = models.BooleanField(default=True)  # Not Implemented yet

    def __str__(self) -> str:
        return str(f"Skill Requirment for {self.group.name}")
