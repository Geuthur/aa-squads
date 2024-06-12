from http import HTTPStatus
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import ImageField, ImageFieldFile
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from squads.forms import SquadsGroupForm
from squads.models.groups import Groups
from squads.models.member import Memberships, Pending
from squads.tests.testdata.load_allianceauth import load_allianceauth
from squads.tests.testdata.load_groups import load_groups, load_membership, load_pending
from squads.tests.testdata.load_users import load_users
from squads.views.application import apply_group, cancel_group, leave_group
from squads.views.main import squads_index, squads_membership, squads_pending
from squads.views.manage import (
    delete_group,
    delete_membership,
    edit_group,
    manage_application_accept,
    manage_application_decline,
    manage_groups,
    manage_members,
    manage_pendings,
)


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_users()
        load_groups()
        cls.factory = RequestFactory()
        cls.user = User.objects.get(username="groupuser")
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", cls.user)

    def test_view(self):
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:index"))
        request.user = self.user
        response = squads_index(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_membership(self):
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:membership"))
        request.user = self.user
        response = squads_membership(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pending(self):
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:pending"))
        request.user = self.user
        response = squads_pending(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestGroupTests(TestCase):
    @classmethod
    def setUp(cls):
        load_allianceauth()
        load_users()
        load_groups()
        cls.factory = RequestFactory()
        cls.user = User.objects.get(username="groupuser")
        cls.user2 = User.objects.get(username="groupuser2")
        cls.group = Groups.objects.get(id=1)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", cls.user)

    @patch("squads.views.application.messages")
    def test_apply_group_no_valid_post(self, mock_messages):
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:apply_group", args=[self.group.pk]),
            {"novalid": True, "comment": "Test Comment"},
        )
        request.user = self.user
        response = apply_group(request, self.group.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Pending.objects.count(), 0)

    @patch("squads.views.application.messages")
    def test_apply_group(self, mock_messages):
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:apply_group", args=[self.group.pk]),
            {"apply_group": True, "comment": "Test Comment"},
        )
        request.user = self.user
        response = apply_group(request, self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Pending.objects.count(), 1)
        self.assertEqual(Pending.objects.first().comment, "Test Comment")
        self.assertEqual(Pending.objects.first().group, self.group)

    @patch("squads.views.application.messages")
    @patch("squads.views.application.CommentForm")
    def test_apply_group_with_comment(self, mock_comment_form, mock_messages):
        # given
        mock_comment_form.return_value.is_valid.return_value = False
        mock_comment_form.return_value.cleaned_data.get.return_value = "Test Comment"

        request = self.factory.post(
            reverse("squads:apply_group", args=[self.group.pk]),
            {"apply_group": True, "comment": "Test Comment"},
        )
        request.user = self.user

        # when
        response = apply_group(request, self.group.pk)
        # then
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertEqual(Pending.objects.count(), 1)
        pending = Pending.objects.first()
        self.assertEqual(pending.comment, "")
        self.assertEqual(pending.group, self.group)
        self.assertEqual(pending.user, self.user)

        mock_messages.success.assert_called_once()

    @patch("squads.views.application.messages")
    def test_apply_group_join(self, mock_messages):
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:apply_group", args=[self.group.pk]),
            {
                "join_group": True,
            },
        )
        request.user = self.user
        response = apply_group(request, self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Pending.objects.count(), 0)
        self.assertEqual(Memberships.objects.count(), 1)
        self.assertEqual(Memberships.objects.first().group, self.group)

    @patch("squads.views.application.messages")
    def test_leave_group(self, mock_messages):
        Memberships.objects.create(group=self.group, user=self.user, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(reverse("squads:leave_group", args=[self.group.pk]))
        request.user = self.user
        response = leave_group(request, self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Memberships.objects.count(), 0)

        mock_messages.warning.assert_called_once()

    @patch("squads.views.application.messages")
    def test_leave_group_not_in_squad(self, mock_messages):
        Memberships.objects.create(group=self.group, user=self.user2, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(reverse("squads:leave_group", args=[self.group.pk]))
        request.user = self.user
        response = leave_group(request, self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Memberships.objects.count(), 1)

        mock_messages.error.assert_called_once()

    @patch("squads.views.application.messages")
    def test_cancel_group(self, mock_messages):
        Pending.objects.create(group=self.group, user=self.user, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:cancel_group", args=[self.group.pk])
        )
        request.user = self.user
        response = cancel_group(request, self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Pending.objects.count(), 0)

        mock_messages.warning.assert_called_once()

    @patch("squads.views.application.messages")
    def test_cancel_group_not_applied(self, mock_messages):
        Pending.objects.create(group=self.group, user=self.user2, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:cancel_group", args=[self.group.pk])
        )
        request.user = self.user
        response = cancel_group(request, self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Pending.objects.count(), 1)

        mock_messages.error.assert_called_once()


class TestApplicationManagement(TestCase):
    @classmethod
    def setUp(self):
        load_allianceauth()
        load_users()
        load_groups()
        self.factory = RequestFactory()
        self.user = User.objects.get(username="groupuser")
        self.user2 = User.objects.get(username="groupuser2")
        self.group = Groups.objects.get(id=1)
        self.group2 = Groups.objects.get(id=2)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)

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
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:accept_group", args=["cf2605fa1ff2"])
        )
        request.user = self.user
        # when
        response = manage_application_accept(request, "cf2605fa1ff2")
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
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:decline_group", args=["cf2605fa1ff2"])
        )
        request.user = self.user
        # when
        response = manage_application_decline(request, "cf2605fa1ff2")
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


class TestMembershipManagement(TestCase):
    @classmethod
    def setUp(self):
        load_allianceauth()
        load_users()
        load_groups()
        self.factory = RequestFactory()
        self.user = User.objects.get(username="groupuser")
        self.user2 = User.objects.get(username="groupuser2")
        self.group = Groups.objects.get(id=1)
        self.group2 = Groups.objects.get(id=2)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)

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
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:delete_membership", args=["cf2605fa1ff2"])
        )
        request.user = self.user
        # when
        response = delete_membership(request, "cf2605fa1ff2")
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()


class TestGroupManagement(TestCase):
    @classmethod
    def setUp(self):
        load_allianceauth()
        load_users()
        load_groups()
        self.factory = RequestFactory()
        self.user = User.objects.get(username="groupuser")
        self.user2 = User.objects.get(username="groupuser2")
        self.group = Groups.objects.get(id=1)
        self.group2 = Groups.objects.get(id=2)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", self.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", self.user)

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
        self.client.force_login(self.user)
        request = self.factory.post(reverse("squads:delete_group", args=[2]))
        request.user = self.user
        # when
        response = delete_group(request, 2)
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
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:edit_group", args=[2]),
            {
                "name": "Test Group",
                "description": "Test Description",
                "req_approve": True,
            },
        )
        request.user = self.user
        # when
        response = edit_group(request, 2)
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
    def test_edit_group_no_image(self, mock_messages):
        # given
        self.client.force_login(self.user)
        post_data = {"name": "Test Group", "description": "Test Description"}
        files_data = {"image": None}

        request = self.factory.post(
            reverse("squads:edit_group", args=[1]), data=post_data, FILES=files_data
        )
        request.user = self.user
        # when
        response = edit_group(request, 1)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.success.assert_called_once()
