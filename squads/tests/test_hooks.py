from unittest.mock import MagicMock

from django.test import TestCase

from squads.auth_hooks import SquadsMenuItem
from squads.hooks import get_extension_logger


class TestTemplateTags(TestCase):
    def test_logger_fail(self):
        with self.assertRaises(TypeError):
            get_extension_logger(1234)


class AuthHooksTest(TestCase):
    def test_render_returns_empty_string_for_user_without_permission(self):
        # Setup
        squads_menu_item = SquadsMenuItem()
        mock_request = MagicMock()
        mock_request.user.has_perm.return_value = (
            False  # User does not have the required permission
        )

        # Action
        result = squads_menu_item.render(mock_request)

        # Assert
        self.assertEqual(
            result,
            "",
            "Expected render method to return an empty string for users without permission",
        )
