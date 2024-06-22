from ninja import NinjaAPI

from django.test import TestCase

from app_utils.testing import create_user_from_evecharacter

from squads.api.groups import ManageApiEndpoints
from squads.models import Groups, Pending
from squads.models.member import Memberships
from squads.tests.testdata.load_allianceauth import load_allianceauth
from squads.tests.testdata.load_groups import load_groups, load_membership, load_pending
from squads.tests.testdata.load_users import load_users


class ManageApiEndpointsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_users()
        load_groups()
        load_pending()
        load_membership()

        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
                "squads.squad_manager",
                "squads.squad_admin",
            ],
        )
        cls.group = Groups.objects.get(name="Group No Approve")
        cls.all_groups = Groups.objects.all()

        cls.api = NinjaAPI()
        cls.manage_api_endpoints = ManageApiEndpoints(api=cls.api)

        cls.pending = Pending.objects.get(group=cls.group)
        cls.all_pendings = Pending.objects.all()

        cls.member = Memberships.objects.get(group=cls.group)
        cls.all_memberships = Memberships.objects.all()

    def test_get_pendings_group_id(self):
        self.client.force_login(self.user)
        url = f"/squads/api/groups/{self.group.pk}/pendings/"

        response = self.client.get(url)

        expected_data = [
            {
                "group": self.pending.group.name,
                "group_id": self.pending.group.pk,
                "user": self.pending.user.username,
                "approved": self.pending.approved,
                "req_filters": self.pending.req_filters,
                "application_id": self.pending.application_id,
                "comment": self.pending.comment,
                "created_at": self.pending.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[
                    :-4
                ]
                + "Z",
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_pendings_all(self):
        self.client.force_login(self.user)
        url = "/squads/api/groups/0/pendings/"

        response = self.client.get(url)
        expected_data = []

        for pending in self.all_pendings:
            expected_data.append(
                {
                    "group": pending.group.name,
                    "group_id": pending.group.pk,
                    "user": pending.user.username,
                    "approved": pending.approved,
                    "req_filters": pending.req_filters,
                    "application_id": pending.application_id,
                    "comment": pending.comment,
                    "created_at": pending.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[
                        :-4
                    ]
                    + "Z",
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_memberships_group_id(self):
        self.client.force_login(self.user)
        url = f"/squads/api/groups/{self.group.pk}/members/"

        response = self.client.get(url)

        expected_data = [
            {
                "group": self.member.group.name,
                "group_id": self.member.group.pk,
                "user": self.member.user.username,
                "req_filters": self.member.req_filters,
                "is_active": self.member.is_active,
                "joined_at": self.member.joined_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[
                    :-4
                ]
                + "Z",
                "application_id": self.member.application_id,
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_memberships_all(self):
        # given
        self.client.force_login(self.user)
        url = "/squads/api/groups/0/members/"
        # when
        response = self.client.get(url)
        # then
        expected_data = []
        for member in self.all_memberships:
            expected_data.append(
                {
                    "group": member.group.name,
                    "group_id": member.group.pk,
                    "user": member.user.username,
                    "req_filters": member.req_filters,
                    "is_active": member.is_active,
                    "joined_at": member.joined_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4]
                    + "Z",
                    "application_id": member.application_id,
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_group_id(self):
        # given
        self.client.force_login(self.user)
        url = f"/squads/api/groups/{self.group.pk}/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [
            {
                "group": self.group.name,
                "group_id": self.group.pk,
                "owner": self.group.owner.username,
                "is_active": self.group.is_active,
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_group_all(self):
        # given
        self.client.force_login(self.user)
        url = "/squads/api/groups/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = []
        for group in self.all_groups:
            expected_data.append(
                {
                    "group": group.name,
                    "group_id": group.pk,
                    "owner": group.owner.username,
                    "is_active": group.is_active,
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)
