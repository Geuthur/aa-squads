"""
Memberships Model
"""

from memberaudit.models import (
    CharacterAsset,
    CharacterSkill,
    CharacterSkillSetCheck,
    SkillSet,
    SkillSetSkill,
)

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveGroup, EveType

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
        """
        Returns:
            bool: True if the user passes the filter, False otherwise.
            list: A list dict of missing skills that the user's Characters do not have.
        """
        missing = []
        required_skills = set(self.skill_sets.all())

        user_skills = CharacterSkillSetCheck.objects.filter(
            character__eve_character__character_ownership__user=user,
            skill_set__in=required_skills,
            failed_required_skills__isnull=True,
        )

        if not user_skills.exists():
            existing_skills = set(user_skills.values_list("skill_set", flat=True))
            missing_skills = required_skills - existing_skills

            for missing_skill in missing_skills:
                skills_with_levels = SkillSetSkill.objects.filter(
                    skill_set=missing_skill
                ).values_list("eve_type", "eve_type__name", "required_level")

                for skill, skill_name, required_level in skills_with_levels:
                    char_skills = CharacterSkill.objects.select_related(
                        "character__eve_character__character_ownership"
                    ).filter(
                        character__eve_character__character_ownership__user=user,
                        eve_type=skill,
                        trained_skill_level__gte=required_level,
                    )

                    if not char_skills.exists():
                        missing.append(
                            {
                                "type": "Skill",
                                "name": skill_name,
                                "amount": f"Lv. {required_level}",
                            }
                        )

        return user_skills.exists(), missing


class AssetsFilter(BaseFilter):
    """AssetsFilter."""

    assets = models.ManyToManyField(
        EveType,
        help_text=_(
            "Users must have at least <strong>one</strong> of the selected assets with <strong>one</strong> character."
        ),
    )

    def check_filter(self, user: User):
        """
        Returns:
            bool: True if the user passes the filter, False otherwise.
            list: A list dict of missing assets that the user's Characters do not have.
        """
        missing = []
        required_assets = set(self.assets.all().values_list("name", flat=True))

        user_assets = CharacterAsset.objects.filter(
            character__eve_character__character_ownership__user=user,
            eve_type__in=self.assets.all(),
        )

        existing_assets = set()
        if user_assets.exists():
            existing_assets = set(user_assets.values_list("eve_type__name", flat=True))

        missing_assets = required_assets - existing_assets

        missing_assets_string = ", ".join(sorted(missing_assets))

        if missing_assets:
            missing.append(
                {
                    "type": "Asset" if len(missing_assets) == 1 else "Asset one of",
                    "name": missing_assets_string,
                    "amount": "",
                }
            )

        return user_assets.exists(), missing


class ShipFilter(BaseFilter):
    """ShipFilter."""

    ship = models.ManyToManyField(
        EveGroup,
        help_text=_(
            "Users must have at least <strong>one</strong> of the selected Ship Type with <strong>one</strong> character."
        ),
    )

    def check_filter(self, user: User):
        """
        Returns:
            bool: True if the user passes the filter, False otherwise.
            list: A list dict of missing Ship Type that the user's Characters do not have.
        """
        missing = []
        required_ship = set(self.ship.all().values_list("name", flat=True))

        user_ship = CharacterAsset.objects.filter(
            character__eve_character__character_ownership__user=user,
            eve_type__eve_group_id__in=self.ship.all(),
        )

        existing_ship = set()
        if user_ship.exists():
            existing_ship = set(user_ship.values_list("eve_group__name", flat=True))

        missing_ship = required_ship - existing_ship

        missing_ship_string = ", ".join(sorted(missing_ship))

        if missing_ship:
            missing.append(
                {"type": "Ship Type", "name": missing_ship_string, "amount": ""}
            )

        return user_ship.exists(), missing


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
        missing_req = []
        for check in self.filters.all():
            try:
                _filter = check.filter_object
                if _filter is None:
                    logger.debug("Filter %s is None", check)
                    continue
                run_test, missing = _filter.check_filter(user)
                missing_req.append(missing)
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
        return output, missing_req

    def process_filters(self, checks):
        output = True
        for check in checks:
            output = output and check.get("result", False)
        return output

    def check_user(self, user: User):
        checks, missing = self.run_filters(user)
        output = self.process_filters(checks)
        logger.debug("Output: %s and Missing: %s", output, missing)
        return output, missing
