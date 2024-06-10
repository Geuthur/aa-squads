import time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from squads.models.groups import Groups
from squads.view_helpers.core import generate_unique_id
from squads.views import _core


class CoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.factory = RequestFactory()
        self.group = Groups.objects.create(owner=self.user, name="Test Group")

    @patch("squads.models.groups.Pending.objects.filter")
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
        """Test that the output is always 12 characters long."""
        unique_id = generate_unique_id()
        self.assertEqual(len(unique_id), 12)

    def test_uniqueness_over_time(self):
        """Test that the function generates unique values over time."""
        unique_ids = set()
        for _ in range(5):
            unique_id = generate_unique_id()
            self.assertNotIn(unique_id, unique_ids)
            unique_ids.add(unique_id)
            time.sleep(0.01)  # Sleep to ensure time-based uniqueness
