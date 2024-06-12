from http import HTTPStatus
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from squads.tests.testdata.load_groups import load_groups
from squads.tests.testdata.load_users import load_users
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
