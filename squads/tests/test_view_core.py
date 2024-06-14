import time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from squads.models.groups import Groups
from squads.tests.testdata.load_users import load_users
from squads.view_helpers.core import generate_unique_id
from squads.views import _core


class CoreTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_users()
        cls.user = User.objects.get(username="groupuser")
        cls.factory = RequestFactory()
        cls.group = Groups.objects.create(owner=cls.user, name="Test Group")

    @patch("squads.models.member.Pending.objects.filter")
    def test_add_info_to_context(self, mock_filter):
        mock_filter.return_value.count.return_value = 5
        request = self.factory.get("/")
        request.user = self.user
        context = _core.add_info_to_context(request, {})
        self.assertEqual(context["pending_count"], 5)

    @patch("squads.models.groups.Groups.objects.visible_to")
    def test_check_permission_true(self, mock_visible_to):
        mock_visible_to.return_value = [self.group]
        request = self.factory.get("/")
        request.user = self.user
        self.assertTrue(_core.check_permission(request, self.group))

    @patch("squads.models.groups.Groups.objects.visible_to")
    def test_check_permission_false(self, mock_visible_to):
        mock_visible_to.return_value = []
        request = self.factory.get("/")
        request.user = self.user
        self.assertFalse(_core.check_permission(request, self.group))


class TestGenerateUniqueId(TestCase):

    def test_length_of_output(self):
        unique_id = generate_unique_id()
        self.assertEqual(len(unique_id), 12)

    def test_uniqueness_over_time(self):
        unique_ids = set()
        for _ in range(5):
            unique_id = generate_unique_id()
            self.assertNotIn(unique_id, unique_ids)
            unique_ids.add(unique_id)
            time.sleep(0.01)  # Sleep to ensure time-based uniqueness
