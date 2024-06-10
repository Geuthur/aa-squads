from unittest.mock import patch

from django.test import TestCase

from squads import __title__, __version__


class TestEsiClientProviderInitialization(TestCase):
    @patch("esi.clients.EsiClientProvider")
    def test_esi_client_provider_initialization(self, mock_esi_client_provider):
        # The esi instance is created when the module is imported, so we need to reload it
        # to apply the mocks. This requires the importlib module.
        import squads.providers

        # Assert that EsiClientProvider was called with the correct app_info_text
        mock_esi_client_provider.assert_called_once_with(
            app_info_text=f"{__title__} v{__version__}"
        )
