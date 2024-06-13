from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from squads.models.groups import Groups
from squads.models.member import Memberships, Pending
from squads.tests.testdata.load_groups import load_groups
from squads.tests.testdata.load_users import load_users
from squads.views.application import apply_group, cancel_group, leave_group


class TestApplictaion(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_users()
        load_groups()
        cls.factory = RequestFactory()
        cls.user = User.objects.get(username="groupuser")
        cls.user2 = User.objects.get(username="groupuser2")
        cls.group = Groups.objects.get(id=1)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", cls.user)

    @patch("squads.views.application.messages")
    def test_apply_group_no_valid_post(self, mock_messages):
        # given
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:apply_group", args=[self.group.pk]),
            {"novalid": True, "comment": "Test Comment"},
        )
        request.user = self.user
        # when
        response = apply_group(request, self.group.pk)
        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Pending.objects.count(), 0)

    @patch("squads.views.application.messages")
    def test_apply_group(self, mock_messages):
        # given
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:apply_group", args=[self.group.pk]),
            {"apply_group": True, "comment": "Test Comment"},
        )
        request.user = self.user
        # when
        response = apply_group(request, self.group.pk)
        # then
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
        # given
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:apply_group", args=[self.group.pk]),
            {
                "join_group": True,
            },
        )
        request.user = self.user
        # when
        response = apply_group(request, self.group.pk)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Pending.objects.count(), 0)
        self.assertEqual(Memberships.objects.count(), 1)
        self.assertEqual(Memberships.objects.first().group, self.group)

    @patch("squads.views.application.messages")
    def test_leave_group(self, mock_messages):
        # given
        Memberships.objects.create(group=self.group, user=self.user, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(reverse("squads:leave_group", args=[self.group.pk]))
        request.user = self.user
        # when
        response = leave_group(request, self.group.pk)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Memberships.objects.count(), 0)

        mock_messages.warning.assert_called_once()

    @patch("squads.views.application.messages")
    def test_leave_group_not_in_squad(self, mock_messages):
        # given
        Memberships.objects.create(group=self.group, user=self.user2, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(reverse("squads:leave_group", args=[self.group.pk]))
        request.user = self.user
        # when
        response = leave_group(request, self.group.pk)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Memberships.objects.count(), 1)
        mock_messages.error.assert_called_once()

    @patch("squads.views.application.messages")
    def test_cancel_group(self, mock_messages):
        # given
        Pending.objects.create(group=self.group, user=self.user, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:cancel_group", args=[self.group.pk])
        )
        request.user = self.user
        # when
        response = cancel_group(request, self.group.pk)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Pending.objects.count(), 0)
        mock_messages.warning.assert_called_once()

    @patch("squads.views.application.messages")
    def test_cancel_group_not_applied(self, mock_messages):
        # given
        Pending.objects.create(group=self.group, user=self.user2, req_filters=False)
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:cancel_group", args=[self.group.pk])
        )
        request.user = self.user
        # when
        response = cancel_group(request, self.group.pk)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Pending.objects.count(), 1)
        mock_messages.error.assert_called_once()
