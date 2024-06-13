from memberaudit.models import (
    Character,
    CharacterSkill,
    CharacterSkillSetCheck,
    SkillSet,
    SkillSetSkill,
)

from django.contrib.contenttypes.models import ContentType
from eveuniverse.models import EveGroup, EveType

from squads.models.filters import (
    AssetsFilter,
    CharacterAsset,
    ShipFilter,
    SkillSetFilter,
    SquadFilter,
    SquadGroup,
)
from squads.models.groups import Groups


def load_filters():
    AssetsFilter.objects.all().delete()
    SkillSetFilter.objects.all().delete()
    ShipFilter.objects.all().delete()

    asset_filter = AssetsFilter.objects.create(description="Naglfar Asset Filter")
    asset_filter.assets.add(EveType.objects.get(name="Naglfar"))
    asset_filter.save()
    filter1 = SquadFilter.objects.create(
        object_id=asset_filter.id,  # Use the ID of the asset_filter instance
        content_type=ContentType.objects.get_for_model(AssetsFilter),
    )

    ship_filter = ShipFilter.objects.create(description="Dreadnought Ship Filter")
    ship_filter.ship.add(EveGroup.objects.get(id=485))
    ship_filter.save()

    skill_set_filter = SkillSetFilter.objects.create(description="SkillSet Filter")
    skill_set = SkillSet.objects.create(name="Shield Management Skill Set")
    SkillSetSkill.objects.create(
        skill_set=skill_set,
        eve_type=EveType.objects.get(name="Shield Management"),
        required_level=3,
    )
    skill_set_filter.skill_sets.add(skill_set)
    skill_set_filter.save()
    filter2 = SquadFilter.objects.create(
        object_id=skill_set_filter.id,  # Use the ID of the asset_filter instance
        content_type=ContentType.objects.get_for_model(SkillSetFilter),
    )

    empty_filter = SquadFilter.objects.create(
        object_id=999,  # Kein object_id und content_type gesetzt
        content_type=ContentType.objects.get_for_model(SkillSetFilter),
    )

    CharacterAsset.objects.create(
        item_id=19722,
        character=Character.objects.get(eve_character__character_id=1001),
        eve_type=EveType.objects.get(name="Naglfar"),
        quantity=1,
        is_singleton=False,
    )
    CharacterAsset.objects.create(
        item_id=19722,
        character=Character.objects.get(eve_character__character_id=1002),
        eve_type=EveType.objects.get(name="Naglfar"),
        quantity=1,
        is_singleton=False,
    )

    CharacterSkill.objects.create(
        character=Character.objects.get(eve_character__character_id=1001),
        eve_type=EveType.objects.get(name="Shield Management"),
        active_skill_level=5,
        trained_skill_level=5,
        skillpoints_in_skill=256000,
    )

    CharacterSkill.objects.create(
        character=Character.objects.get(eve_character__character_id=1002),
        eve_type=EveType.objects.get(name="Shield Management"),
        active_skill_level=5,
        trained_skill_level=5,
        skillpoints_in_skill=256000,
    )

    CharacterSkillSetCheck.objects.create(
        character=Character.objects.get(eve_character__character_id=1001),
        skill_set=skill_set,
    )

    squad1 = SquadGroup.objects.create(
        group=Groups.objects.get(name="Group No Approve"),
        description="A test squad",
    )
    squad1.filters.add(filter1)
    squad1.filters.add(filter2)
    squad1.filters.add(empty_filter)
