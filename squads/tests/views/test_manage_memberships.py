from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from squads.models.groups import Groups
from squads.models.member import Memberships
from squads.tests.testdata.load_groups import load_groups, load_membership
from squads.tests.testdata.load_users import load_users
from squads.views.manage import delete_membership, manage_members


class TestMembershipManagement(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_users()
        load_groups()
        cls.factory = RequestFactory()
        cls.user = User.objects.get(username="groupuser")
        cls.user2 = User.objects.get(username="groupuser2")
        cls.group = Groups.objects.get(id=1)
        cls.group2 = Groups.objects.get(id=2)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", cls.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", cls.user)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", cls.user2)
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", cls.user2)

    def test_manage_members(self):
        # given
        load_membership()
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        # when
        request = self.factory.get(reverse("squads:manage_members"))
        request.user = self.user
        response = manage_members(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch("squads.views.manage.messages")
    def test_delete_membership(self, mock_messages):
        # given
        load_membership()
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:delete_membership", args=["cf2605fa1ff2"])
        )
        request.user = self.user
        # when
        response = delete_membership(request, "cf2605fa1ff2")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(
            Memberships.objects.filter(user=self.user2, group=self.group2).exists()
        )
        mock_messages.success.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_delete_membership_not_exist(self, mock_messages):
        # given
        load_membership()
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:delete_membership", args=["cf2605fa1ff9"])
        )
        request.user = self.user
        # when
        response = delete_membership(request, "cf2605fa1ff9")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_delete_membership_no_permission(self, mock_messages):
        # given
        load_membership()
        self.client.force_login(self.user2)
        request = self.factory.post(
            reverse("squads:delete_membership", args=["cf2605fa1ff3"])
        )
        request.user = self.user2
        # when
        response = delete_membership(request, "cf2605fa1ff3")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()
