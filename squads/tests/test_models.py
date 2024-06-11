from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.html import mark_safe

from squads.models import Groups, Memberships


class GroupsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="12345")

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

    def test_safe_description(self):
        group = Groups.objects.create(
            name="Test Group",
            owner=self.user,
            description='<script>alert("test")</script>',
        )
        self.assertEqual(group.safe_description(), mark_safe(group.description))


class MemberShipModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="12345")

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
