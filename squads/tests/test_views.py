from http import HTTPStatus

from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from app_utils.testing import create_user_from_evecharacter

from squads.tests.testdata.load_allianceauth import load_allianceauth
from squads.views.main import squads_index


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        cls.factory = RequestFactory()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
            ],
        )

    def test_view(self):
        request = self.factory.get(reverse("squads:index"))
        request.user = self.user
        response = squads_index(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
