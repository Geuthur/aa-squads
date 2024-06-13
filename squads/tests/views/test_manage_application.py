from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from squads.models.groups import Groups
from squads.models.member import Memberships, Pending
from squads.tests.testdata.load_groups import load_groups, load_pending
from squads.tests.testdata.load_users import load_users
from squads.views.manage import (
    manage_application_accept,
    manage_application_decline,
    manage_pendings,
)


class TestManageApplicationManagement(TestCase):
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

    @patch("squads.views.manage.messages")
    def test_manage_application_accept(self, mock_messages):
        # given
        load_pending()
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:accept_group", args=["cf2605fa1ff2"])
        )
        request.user = self.user
        # when
        response = manage_application_accept(request, "cf2605fa1ff2")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Memberships.objects.filter(user=self.user2, group=self.group2).exists()
        )
        self.assertFalse(
            Pending.objects.filter(
                user=self.user2, group=self.group2, application_id="cf2605fa1ff2"
            ).exists()
        )
        mock_messages.success.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_manage_application_accept_not_exist(self, mock_messages):
        # given
        load_pending()
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:accept_group", args=["cf2605fa1ff9"])
        )
        request.user = self.user
        # when
        response = manage_application_accept(request, "cf2605fa1ff9")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_manage_application_accept_no_permission(self, mock_messages):
        # given
        load_pending()
        self.client.force_login(self.user2)
        request = self.factory.post(
            reverse("squads:accept_group", args=["cf2605fa1ff3"])
        )
        request.user = self.user2
        # when
        response = manage_application_accept(request, "cf2605fa1ff3")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_manage_application_decline(self, mock_messages):
        # given
        load_pending()
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:decline_group", args=["cf2605fa1ff2"])
        )
        request.user = self.user
        # when
        response = manage_application_decline(request, "cf2605fa1ff2")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(
            Pending.objects.filter(
                user=self.user2, group=self.group2, application_id="cf2605fa1ff2"
            ).exists()
        )
        mock_messages.success.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_manage_application_decline_not_exist(self, mock_messages):
        # given
        load_pending()
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:decline_group", args=["cf2605fa1ff9"])
        )
        request.user = self.user
        # when
        response = manage_application_decline(request, "cf2605fa1ff9")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_manage_application_decline_no_permission(self, mock_messages):
        # given
        load_pending()
        self.client.force_login(self.user2)
        request = self.factory.post(
            reverse("squads:decline_group", args=["cf2605fa1ff3"])
        )
        request.user = self.user2
        # when
        response = manage_application_decline(request, "cf2605fa1ff3")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    def test_manage_pendings(self):
        # given
        load_pending()
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        # when
        request = self.factory.get(reverse("squads:manage_pendings"))
        request.user = self.user
        response = manage_pendings(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
