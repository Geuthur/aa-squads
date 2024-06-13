# Import necessary modules and classes
from memberaudit.models import Character

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase
from eveuniverse.models import EveType

from squads.admin import AssetsFilterAdmin, SkillSetFilterAdmin
from squads.models.filters import AssetsFilter, CharacterAsset, SkillSet, SkillSetFilter
from squads.tests.testdata.load_eveuniverse import load_eveuniverse
from squads.tests.testdata.load_memberaudit import load_memberaudit
from squads.tests.testdata.load_users import load_users


class SkillSetFilterAdminTest(TestCase):
    def setUp(self):
        # Setup test environment
        self.site = AdminSite()
        load_users()
        self.user = User.objects.get(username="groupuser4")

        # Create test data
        self.skill_set_filter = SkillSetFilter.objects.create(description="Test Filter")
        self.skill_set = SkillSet.objects.create(name="Test Skill Set")
        self.skill_set_filter.skill_sets.add(self.skill_set)

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
