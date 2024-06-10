from django.contrib.auth.models import Permission
from django.test import TestCase

from app_utils.testing import create_user_from_evecharacter

from squads.models.groups import Groups
from squads.tests.testdata.load_allianceauth import load_allianceauth


class GroupsManagerTest(TestCase):
    def setUp(self):
        load_allianceauth()
        self.groups = Groups.objects
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
            ],
        )
        self.user2, self.character_ownership = create_user_from_evecharacter(
            1002,
            permissions=[
                "squads.basic_access",
            ],
        )
        Groups.objects.create(
            name="Test Squad",
            description="Test Squad Description",
            owner=self.user2,
        )
        Groups.objects.create(
            name="Test Squad 2",
            description="Test Squad Description",
            owner=self.user,
        )

    def test_visible_to_superuser(self):
        self.user.is_superuser = True
        visible_squads = self.groups.visible_to(self.user)
        self.assertEqual(visible_squads.count(), Groups.objects.count())

    def test_visible_to_squad_admin(self):
        permission, _ = Permission.objects.get_or_create(codename="squad_admin")
        self.user.user_permissions.add(permission)
        visible_squads = self.groups.visible_to(self.user)
        self.assertEqual(visible_squads.count(), Groups.objects.count())

    def test_visible_to_squad_manager(self):
        permission, _ = Permission.objects.get_or_create(codename="squad_manager")
        self.user.user_permissions.add(permission)
        visible_squads = self.groups.visible_to(self.user)
        self.assertEqual(visible_squads.count(), 1)  # Only owns 1 squad

    def test_visible_to_regular_user(self):
        visible_squads = self.groups.visible_to(self.user)
        self.assertEqual(visible_squads.count(), 0)  # Should see none
