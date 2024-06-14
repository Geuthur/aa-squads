# Import necessary modules and classes
from memberaudit.models import Character

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase
from eveuniverse.models import EveGroup, EveType

from squads.admin import (
    AssetsFilterAdmin,
    ShipFilterForm,
    ShippFilterAdmin,
    SkillSetFilterAdmin,
    SquadFilterAdmin,
)
from squads.models.filters import (
    AssetsFilter,
    CharacterAsset,
    ShipFilter,
    SkillSet,
    SkillSetFilter,
    SquadFilter,
)
from squads.tests.testdata.load_allianceauth import load_allianceauth
from squads.tests.testdata.load_eveuniverse import load_eveuniverse
from squads.tests.testdata.load_memberaudit import load_memberaudit
from squads.tests.testdata.load_users import load_users


class SkillSetFilterAdminTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Setup test environment
        cls.site = AdminSite()
        load_users()
        cls.user = User.objects.get(username="groupuser4")

        # Create test data
        cls.skill_set_filter = SkillSetFilter.objects.create(description="Test Filter")
        cls.skill_set = SkillSet.objects.create(name="Test Skill Set")
        cls.skill_set_filter.skill_sets.add(cls.skill_set)

    def test_skill_sets_display(self):
        self.client.force_login(self.user)

        admin = SkillSetFilterAdmin(SkillSetFilter, self.site)

        result = admin._skill_sets(self.skill_set_filter)

        # Assert the expected result
        self.assertEqual(result, "Test Skill Set")

    def test_skill_queryset(self):
        self.client.force_login(self.user)

        admin = SkillSetFilterAdmin(SkillSetFilter, self.site)

        # Call the get_queryset method
        result = admin.get_queryset(self.site)

        # Assert the expected result
        self.assertIsNotNone(result)


class AssetFilterAdminTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.site = AdminSite()
        load_users()
        load_allianceauth()
        load_eveuniverse()
        load_memberaudit()
        cls.user = User.objects.get(username="groupuser4")

        # Create test data
        cls.asset_filter = AssetsFilter.objects.create(description="Test Filter")
        cls.character = Character.objects.first()
        cls.asset = CharacterAsset.objects.create(
            item_id=19722,
            character=cls.character,
            eve_type=EveType.objects.get(name="Naglfar"),
            quantity=1,
            is_singleton=False,
        )
        cls.asset_filter.assets.add(EveType.objects.get(name="Naglfar"))

    def test_assets_display(self):
        self.client.force_login(self.user)

        admin = AssetsFilterAdmin(AssetsFilter, self.site)

        result = admin._assets(self.asset_filter)

        # Assert the expected result
        self.assertEqual(result, "Naglfar")

    def test_asset_queryset(self):
        self.client.force_login(self.user)

        admin = AssetsFilterAdmin(AssetsFilter, self.site)

        # Call the get_queryset method
        result = admin.get_queryset(self.site)

        # Assert the expected result
        self.assertIsNotNone(result)


class ShipFilterAdminTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Setup test environment
        cls.site = AdminSite()
        load_users()
        load_allianceauth()
        load_eveuniverse()
        load_memberaudit()
        cls.user = User.objects.get(username="groupuser4")

        # Create test data
        cls.ship_filter = ShipFilter.objects.create(description="Test Filter")
        cls.character = Character.objects.first()
        cls.asset = CharacterAsset.objects.create(
            item_id=19722,
            character=cls.character,
            eve_type=EveType.objects.get(name="Naglfar"),
            quantity=1,
            is_singleton=False,
        )
        cls.ship_filter.ship.add(EveGroup.objects.get(id=485))

    def test_ship_display(self):
        self.client.force_login(self.user)

        admin = ShippFilterAdmin(ShipFilter, self.site)

        result = admin._ship(self.ship_filter)

        # Assert the expected result
        self.assertEqual(result, "Dreadnought")

    def test_ship_queryset(self):
        self.client.force_login(self.user)

        admin = ShippFilterAdmin(ShipFilter, self.site)

        # Call the get_queryset method
        result = admin.get_queryset(self.site)

        # Assert the expected result
        self.assertIsNotNone(result)

    def test_ship_field_queryset(self):
        form = ShipFilterForm()
        ship_field_qs = form.fields["ship"].queryset

        # Verify queryset
        self.assertTrue(ship_field_qs.filter(name="Dreadnought").exists())
        self.assertFalse(ship_field_qs.filter(name="Structure").exists())
        self.assertFalse(ship_field_qs.filter(name="Planet").exists())


class SquadFilterAdminTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_users()
        cls.site = AdminSite()
        cls.user = User.objects.get(username="groupuser4")

    def test_has_add_permission(self):
        # Create an instance of the admin class
        admin = SquadFilterAdmin(SquadFilter, self.site)

        # Create a mock request object
        request = self.user

        # Call the has_add_permission method and assert the result is False
        self.assertFalse(admin.has_add_permission(request))
