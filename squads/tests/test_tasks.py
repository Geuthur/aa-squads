from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from squads.models.groups import Groups
from squads.models.member import Memberships, Pending
from squads.tasks import run_check_members, run_check_pendings, run_check_squads
from squads.tests.testdata.load_groups import load_groups, load_membership, load_pending
from squads.tests.testdata.load_users import load_users


class TestTasks(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        load_users()
        load_groups()
        load_membership()
        load_pending()

    @patch("squads.tasks.logger")
    def test_run_check_squads(self, mock_logger):
        # given/when
        run_check_squads()
        # then
        mock_logger.info.assert_called_with("Check Squads runs completed: %s", 2)

    @patch("squads.tasks.SquadGroup.objects.filter")
    def test_run_check_members(self, mock_squadgroup_filter):
        # given
        mock_filter = MagicMock()
        mock_filter.check_user.return_value = (True, None)
        mock_squadgroup_filter.return_value.first.return_value = mock_filter
        user = User.objects.get(username="groupuser")
        member_actual = Memberships.objects.get(user=user)
        # when
        result = run_check_members(1)
        # then
        member_then = Memberships.objects.get(user=user)
        self.assertFalse(member_actual.req_filters)
        self.assertTrue(member_then.req_filters)
        self.assertTrue(result)

    @patch("squads.tasks.SquadGroup.objects.filter")
    def test_run_check_members_fail_check(self, mock_squadgroup_filter):
        # given
        mock_filter = MagicMock()
        mock_filter.check_user.return_value = (False, None)
        mock_squadgroup_filter.return_value.first.return_value = mock_filter
        user = User.objects.get(username="groupuser2")
        member_actual = Memberships.objects.get(user=user)
        # when
        result = run_check_members(2)
        # then
        member_then = Memberships.objects.get(user=user)
        self.assertTrue(member_actual.req_filters)
        self.assertFalse(member_then.req_filters)
        self.assertTrue(result)

    @patch("squads.tasks.SquadGroup.objects.filter")
    def test_run_check_members_no_filters(self, mock_squadgroup_filter):
        # given
        mock_squadgroup_filter.return_value.first.return_value = False
        # when
        result = run_check_members(1)
        # then
        self.assertFalse(result)

    @patch("squads.tasks.SquadGroup.objects.filter")
    def test_run_check_pending(self, mock_squadgroup_filter):
        # given
        mock_filter = MagicMock()
        mock_filter.check_user.return_value = (True, None)
        mock_squadgroup_filter.return_value.first.return_value = mock_filter
        user = User.objects.get(username="groupuser")
        pending_actual = Pending.objects.get(user=user)
        # when
        result = run_check_pendings(1)
        # then
        pending_then = Pending.objects.get(user=user)
        self.assertFalse(pending_actual.req_filters)
        self.assertTrue(pending_then.req_filters)
        self.assertTrue(result)

    @patch("squads.tasks.SquadGroup.objects.filter")
    def test_run_check_pending_fail_check(self, mock_squadgroup_filter):
        # given
        mock_filter = MagicMock()
        mock_filter.check_user.return_value = (False, None)
        mock_squadgroup_filter.return_value.first.return_value = mock_filter
        user = User.objects.get(username="groupuser2")
        pending_actual = Pending.objects.get(user=user)
        # when
        result = run_check_pendings(2)
        # then
        pending_then = Pending.objects.get(user=user)
        self.assertTrue(pending_actual.req_filters)
        self.assertFalse(pending_then.req_filters)
        self.assertTrue(result)

    @patch("squads.tasks.SquadGroup.objects.filter")
    def test_run_check_pending_no_filters(self, mock_squadgroup_filter):
        # given
        mock_squadgroup_filter.return_value.first.return_value = False
        # when
        result = run_check_pendings(1)
        # then
        self.assertFalse(result)
