from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from squads.models.groups import Groups
from squads.tests.testdata.load_groups import load_groups
from squads.tests.testdata.load_users import load_users
from squads.views.manage import delete_group, edit_group, manage_groups


class TestGroupManagement(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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

    def test_manage_groups(self):
        # given
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        # when
        request = self.factory.get(reverse("squads:manage_groups"))
        request.user = self.user
        response = manage_groups(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch("squads.views.manage.messages")
    def test_delete_group(self, mock_messages):
        # given
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(reverse("squads:delete_group", args=[1]))
        request.user = self.user
        # when
        response = delete_group(request, 1)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Groups.objects.filter(id=1).exists())
        mock_messages.success.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_delete_group_not_exist(self, mock_messages):
        # given
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(reverse("squads:delete_group", args=[9]))
        request.user = self.user
        # when
        response = delete_group(request, 9)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_delete_group_no_permission(self, mock_messages):
        # given
        self.client.force_login(self.user2)
        request = self.factory.post(reverse("squads:delete_group", args=[3]))
        request.user = self.user2
        # when
        response = delete_group(request, 3)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_edit_group(self, mock_messages):
        # given
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:edit_group", args=[1]),
            {
                "name": "Test Group",
                "description": "Test Description",
                "req_approve": True,
            },
        )
        request.user = self.user
        # when
        response = edit_group(request, 1)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Groups.objects.filter(
                id=1,
                name="Test Group",
                description="Test Description",
                req_approve=True,
            ).exists()
        )
        mock_messages.success.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_edit_group_not_exist(self, mock_messages):
        # given
        AuthUtils.add_permission_to_user_by_name("squads.squad_admin", self.user)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:edit_group", args=[9]),
            {
                "name": "Test Group",
                "description": "Test Description",
                "req_approve": True,
            },
        )
        request.user = self.user
        # when
        response = edit_group(request, 9)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_edit_group_no_permission(self, mock_messages):
        # given
        self.client.force_login(self.user2)
        request = self.factory.post(
            reverse("squads:edit_group", args=[3]),
            {
                "name": "Test Group",
                "description": "Test Description",
                "req_approve": True,
            },
        )
        request.user = self.user2
        # when
        response = edit_group(request, 3)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_edit_group_invalid_form(self, mock_messages):
        # given
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:edit_group", args=[1]),
            {"name": "", "description": "Test Description"},
        )
        request.user = self.user
        # when
        response = edit_group(request, 1)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_messages.error.assert_called_once()

    @patch("squads.views.manage.messages")
    def test_edit_group_no_post(self, mock_messages):
        # given
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:edit_group", args=[1]))
        request.user = self.user
        # when
        response = edit_group(request, 1)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch("squads.views.manage.messages")
    def test_edit_group_with_image(self, mock_messages):
        # given
        self.client.force_login(self.user)
        group = Groups.objects.get(id=1)
        group.image = "existing/image.png"
        group.save()
        request = self.factory.post(
            reverse("squads:edit_group", args=[1]),
            {"name": "Test Group", "description": "Test Description"},
        )
        request.user = self.user
        # when
        response = edit_group(request, 1)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.success.assert_called_once()
