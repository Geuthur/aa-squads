"""
Memberships Model
"""

from memberaudit.models import CharacterAsset, CharacterSkillSetCheck, SkillSet

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveType

from squads.hooks import get_extension_logger
from squads.models.groups import Groups

logger = get_extension_logger(__name__)


class BaseFilter(models.Model):
    """BaseFilter Model."""

    description = models.CharField(
        max_length=500,
        help_text=_("Filter Name."),
    )

    def __str__(self) -> str:
        return str(self.description)

    class Meta:
        abstract = True


class SkillSetFilter(BaseFilter):
    """SkillSetFilter."""

    skill_sets = models.ManyToManyField(
        SkillSet,
        help_text=_(
            "Users must possess the selected skill sets with at least <strong>one</strong> character."
        ),
        related_name="squads_skill_sets",
    )

    def check_filter(self, user: User):
        """Check if user Characters has required skills."""
        qs = CharacterSkillSetCheck.objects.filter(
            character__eve_character__character_ownership__user=user,
            skill_set__in=list(self.skill_sets.all()),
            failed_required_skills__isnull=True,
        )
        return qs.exists()


class AssetsFilter(BaseFilter):
    """AssetsFilter."""

    assets = models.ManyToManyField(
        EveType,
        help_text=_(
            "Users must have at least <strong>one</strong> of the selected assets with <strong>one</strong> character."
        ),
    )

    def check_filter(self, user: User):
        """Check if user Characters has at least one of the given asset."""
        return CharacterAsset.objects.filter(
            character__eve_character__character_ownership__user=user,
            eve_type__in=list(self.assets.all()),
        ).exists()


class SquadFilter(models.Model):
    """SquadFilter show up all Filters."""

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, editable=False
    )
    object_id = models.PositiveIntegerField(editable=False)
    filter_object = GenericForeignKey("content_type", "object_id")

    def __str__(self) -> str:
        return str(self.filter_object)

    class Meta:
        verbose_name = "Squad Filter"


class SquadGroup(models.Model):
    """Squads Group Filter."""

    group = models.OneToOneField(Groups, on_delete=models.CASCADE)
    description = models.CharField(max_length=500, default="", blank=True)
    filters = models.ManyToManyField(SquadFilter)
    enabled = models.BooleanField(default=True)  # Not Implemented yet
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(f"Filter Group: {self.group.name}")

    # Check Filters
    # pylint: disable=broad-exception-caught
    def run_filters(self, user: User):
        output = []
        for check in self.filters.all():
            try:
                _filter = check.filter_object
                if _filter is None:
                    logger.debug("Filter %s is None", check)
                    continue
                run_test = _filter.check_filter(user)
            except Exception as e:
                run_test = False
                logger.warning("Filter Check Failed: %s", check)
                logger.debug("Error: %s", e, exc_info=True)
            _check = {
                "desc": check.filter_object.description,
            }
            _check["result"] = run_test
            _check["filter"] = check
            output.append(_check)
        return output

    def process_filters(self, checks):
        output = True
        for check in checks:
            output = output and check.get("result", False)
        return output

    def check_user(self, user: User):
        checks = self.run_filters(user)
        output = self.process_filters(checks)
        return output
