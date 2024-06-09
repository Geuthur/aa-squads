from unittest.mock import patch

from django.test import TestCase

from app_utils.esi import EsiDailyDowntime

from squads.decorators import when_esi_is_available


class TestDecorators(TestCase):
    @patch("squads.decorators.fetch_esi_status")
    @patch("squads.decorators.IS_TESTING", new=False)
    def test_when_esi_is_available(self, mock_fetch_esi_status):
        # given
        @when_esi_is_available
        def trigger_esi_deco():
            return "Esi is Available"

        # when
        result = trigger_esi_deco()
        # then
        mock_fetch_esi_status.assert_called_once()
        self.assertEqual(result, "Esi is Available")

    @patch("squads.decorators.fetch_esi_status", side_effect=EsiDailyDowntime)
    @patch("squads.decorators.IS_TESTING", new=False)
    def test_when_esi_is_available_downtime(self, mock_fetch_esi_status):
        # given
        @when_esi_is_available
        def trigger_esi_deco():
            return "Daily Downtime detected. Aborting."

        # when
        result = trigger_esi_deco()
        # then
        self.assertIsNone(result)

    @patch("squads.decorators.fetch_esi_status")
    @patch("squads.decorators.IS_TESTING", new=True)
    def test_when_esi_is_available_is_test(self, mock_fetch_esi_status):
        # given
        @when_esi_is_available
        def trigger_esi_deco():
            return "Teesting Mode."

        # when
        result = trigger_esi_deco()
        # then
        self.assertEqual(result, "Teesting Mode.")
