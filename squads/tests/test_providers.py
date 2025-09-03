# Standard Library
from unittest.mock import patch

# Django
from django.test import TestCase

# AA Squads
from squads import __app_name_useragent__, __github_url__, __title__, __version__


class TestEsiClientProviderInitialization(TestCase):
    @patch("esi.clients.EsiClientProvider")
    def test_esi_client_provider_initialization(self, mock_esi_client_provider):
        # The esi instance is created when the module is imported, so we need to reload it
        # to apply the mocks. This requires the importlib module.
        # AA Squads
        import squads.providers

        # Assert that EsiClientProvider was called with the correct arguments
        mock_esi_client_provider.assert_called_once_with(
            ua_appname=__app_name_useragent__,
            ua_version=__version__,
            ua_url=__github_url__,
        )
