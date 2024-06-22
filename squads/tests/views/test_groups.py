from http import HTTPStatus
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from squads.models import Groups
from squads.tests.testdata.load_groups import load_groups
from squads.tests.testdata.load_users import load_users
from squads.views.groups import broswe_groups, create_group, view_group


class GroupViewTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_users()
        load_groups()
        cls.factory = RequestFactory()
        cls.user = User.objects.get(username="groupuser")
        cls.user2 = User.objects.get(username="groupuser2")
        cls.group = Groups.objects.get(id=1)
        AuthUtils.add_permission_to_user_by_name("squads.basic_access", cls.user)
        AuthUtils.add_permission_to_user_by_name("squads.squad_manager", cls.user)

    @patch("squads.views.groups.messages")
    def test_create_group(self, mock_messages):
        # given
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:create_group"),
            {
                "name": "New Test Group",
                "description": "Test Description",
                "req_approve": True,
            },
        )
        request.user = self.user
        # when
        response = create_group(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Groups.objects.filter(
                name="New Test Group",
                description="Test Description",
                req_approve=True,
            ).exists()
        )
        mock_messages.success.assert_called_once()

    def test_create_group_invalid_form(self):
        # given
        self.client.force_login(self.user)
        request = self.factory.post(
            reverse("squads:create_group"),
            {
                "name": "",
                "description": "Test Description",
                "req_approve": True,
            },
        )
        request.user = self.user
        # when
        response = create_group(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Groups.objects.filter(
                name="New Test Group",
                description="Test Description",
                req_approve=True,
            ).exists()
        )

    def test_create_group_no_post(self):
        # given
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:create_group"))
        request.user = self.user
        # when
        response = create_group(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Groups.objects.filter(
                name="New Test Group",
                description="Test Description",
                req_approve=True,
            ).exists()
        )

    @patch("squads.views.groups.messages")
    @patch("squads.views.groups.SquadsGroupForm")
    def test_create_group_with_image(self, mock_group, mock_messages):
        # given
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.force_login(self.user)
        image_path = finders.find("squads/groups_images/empty.png")
        with open(image_path, "rb") as img:
            uploaded_image = SimpleUploadedFile(
                name="empty.png", content=img.read(), content_type="image/png"
            )
        mock_group = MagicMock()
        mock_group.is_valid.return_value = True
        mock_group.save.return_value = Groups(
            name="New Test Group2",
            description="Test Description",
            req_approve=True,
            image=uploaded_image,
        )
        data = {
            "name": "New Test Group2",
            "description": "Test Description",
            "req_approve": True,
            "image": uploaded_image,
        }
        request = self.factory.post(reverse("squads:create_group"), data)
        request.user = self.user
        request.FILES["image"] = uploaded_image
        # when
        response = create_group(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.success.assert_called_once()

    def test_browse_groups(self):
        # given
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:groups"))
        request.user = self.user
        # when
        response = broswe_groups(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Group Approve")
        self.assertNotContains(response, "Group No Approve")
        self.assertContains(response, "Group Superuser")
        self.assertNotContains(response, "Group Staff")

    def test_browse_groups_many_pages(self):
        # given
        for i in range(70):
            Groups.objects.create(owner=self.user, name=f"Group {i}", is_active=True)
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:groups"), {"page": "1"})
        request.user = self.user
        # when
        response = broswe_groups(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Group 50")
        # given 2
        request = self.factory.get(reverse("squads:groups"), {"page": "2"})
        request.user = self.user
        # when 2
        response = broswe_groups(request)
        # then 2
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Group 60")

    def test_browse_groups_empty_page(self):
        # given
        for i in range(70):
            Groups.objects.create(owner=self.user, name=f"Group {i}", is_active=True)
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:groups"), {"page": "999"})
        request.user = self.user
        # when
        response = broswe_groups(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Group 60")

    def test_view_group(self):
        # given
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:view_group", args=[2]))
        request.user = self.user
        # when
        response = view_group(request, 2)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Group Approve")

    @patch("squads.views.groups.SquadGroup.objects.filter")
    def test_view_group_filter(self, mock_filter):
        # given
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:view_group", args=[2]))
        request.user = self.user
        mock_first = MagicMock()
        mock_first.check_user.return_value = (True, ["Test Filter"])

        mock_filter.return_value.first.return_value = mock_first

        # when
        response = view_group(request, 2)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Group Approve")

    @patch("squads.views.groups.messages")
    def test_view_group_not_exist(self, mock_messages):
        # given
        self.client.force_login(self.user)
        request = self.factory.get(reverse("squads:view_group", args=[9]))
        request.user = self.user
        # when
        response = view_group(request, 9)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()
