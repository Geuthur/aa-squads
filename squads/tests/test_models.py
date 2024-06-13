from unittest.mock import PropertyMock, patch

from django.test import TestCase

from app_utils.testing import create_user_from_evecharacter

from squads.models import Groups, Memberships, Pending, filters
from squads.tests.testdata.load_allianceauth import load_allianceauth
from squads.tests.testdata.load_eveuniverse import load_eveuniverse
from squads.tests.testdata.load_filters import load_filters
from squads.tests.testdata.load_groups import load_groups
from squads.tests.testdata.load_memberaudit import load_memberaudit
from squads.tests.testdata.load_users import load_users


class GroupsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_memberaudit()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
            ],
        )

    def test_group_creation(self):
        group = Groups.objects.create(
            name="Test Group",
            owner=self.user,
            description="A test group",
        )
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.owner, self.user)
        self.assertEqual(group.description, "A test group")
        self.assertTrue(group.is_active)
        self.assertFalse(group.req_approve)
        self.assertIsNotNone(group.created_at)
        self.assertIsNotNone(group.updated_at)

    def test_str_method(self):
        group = Groups.objects.create(name="Test Group", owner=self.user)
        self.assertEqual(str(group), "Test Group")


class MemberShipModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_memberaudit()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
            ],
        )

    def test_membership_creation(self):
        group = Groups.objects.create(name="Test Group", owner=self.user)
        membership = Memberships.objects.create(group=group, user=self.user)
        self.assertEqual(membership.group, group)
        self.assertEqual(membership.user, self.user)
        self.assertIsNotNone(membership.joined_at)

    def test_str_method(self):
        group = Groups.objects.create(name="Test Group", owner=self.user)
        membership = Memberships.objects.create(group=group, user=self.user)
        self.assertEqual(str(membership), f"{membership.user} in {membership.group}")


class PendingModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_memberaudit()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
            ],
        )

    def test_pending_creation(self):
        group = Groups.objects.create(name="Test Group", owner=self.user)
        pending = Pending.objects.create(group=group, user=self.user)
        self.assertEqual(pending.group, group)
        self.assertEqual(pending.user, self.user)
        self.assertIsNotNone(pending.created_at)

    def test_str_method(self):
        group = Groups.objects.create(name="Test Group", owner=self.user)
        pending = Pending.objects.create(group=group, user=self.user)
        self.assertEqual(str(pending), f"{pending.user} pending {pending.group}")


class FilterModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()
        load_memberaudit()
        load_users()
        try:
            load_groups()
            load_filters()
        except Exception as e:
            print(e)

        cls.user, _ = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
            ],
        )
        cls.user2, _ = create_user_from_evecharacter(
            1004,
            permissions=[
                "squads.basic_access",
            ],
        )
        cls.user3, _ = create_user_from_evecharacter(
            1002,
            permissions=[
                "squads.basic_access",
            ],
        )

    def test_squad_group_str_method(self):
        # given/when
        filter = filters.SquadGroup.objects.first()
        # then
        self.assertEqual(str(filter), f"Filter Group: {filter.group.name}")

    def test_squad_filter_str_method(self):
        # given/when
        filter = filters.SquadFilter.objects.first()
        # then
        self.assertEqual(str(filter), f"{filter.filter_object}")

    def test_skill_check_filter_valid(self):
        # given
        filter = filters.SkillSetFilter.objects.first()
        # when
        filter_req, _ = filter.check_filter(self.user)
        # then
        self.assertTrue(filter_req)

    def test_skill_check_filter_not_valid_but_skilled(self):
        # given
        filter = filters.SkillSetFilter.objects.first()
        # when
        filter_req, _ = filter.check_filter(self.user3)
        # then
        self.assertFalse(filter_req)

    def test_skill_check_filter_not_valid(self):
        # given
        filter = filters.SkillSetFilter.objects.first()
        # when
        filter_req, _ = filter.check_filter(self.user2)
        # then
        self.assertFalse(filter_req)

    def test_asset_check_filter_valid(self):
        # given
        filter = filters.AssetsFilter.objects.first()
        # when
        filter_req, _ = filter.check_filter(self.user)
        # then
        self.assertTrue(filter_req)

    def test_asset_check_filter_not_valid(self):
        # given
        filter = filters.AssetsFilter.objects.first()
        # when
        filter_req, _ = filter.check_filter(self.user2)
        # then
        self.assertFalse(filter_req)

    def test_ship_check_filter_valid(self):
        # given
        filter = filters.ShipFilter.objects.first()
        # when
        filter_req, _ = filter.check_filter(self.user)
        # then
        self.assertTrue(filter_req)

    def test_ship_check_filter_not_valid(self):
        # given
        filter = filters.ShipFilter.objects.first()
        # when
        filter_req, _ = filter.check_filter(self.user2)
        # then
        self.assertFalse(filter_req)

    def test_squad_run_filters(self):
        # given
        group = filters.SquadGroup.objects.first()
        # when
        filter_req, _ = group.check_user(self.user)
        # then
        self.assertTrue(filter_req)

    def test_squad_run_filters_not_valid(self):
        # given
        group = filters.SquadGroup.objects.first()
        # when
        filter_req, _ = group.check_user(self.user2)
        # then
        self.assertFalse(filter_req)

    @patch("squads.models.filters.SquadFilter.filter_object")
    def test_squad_run_filters_error_filter(self, mock_filter_object):
        # given
        group = filters.SquadGroup.objects.first()
        mock_filter_object.check_filter.side_effect = Exception("Error")
        # when
        filter_req, _ = group.check_user(self.user2)
        # then
        self.assertFalse(filter_req)
