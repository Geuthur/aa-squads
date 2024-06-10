from unittest.mock import MagicMock, patch

from django.test import TestCase

from squads.models.filters import AssetsFilter, SkillSetFilter
from squads.signals import HookCache, new_filter, rem_filter


class TestHookCache(TestCase):
    @patch("squads.signals.hooks.get_hooks")
    def test_get_hooks(self, mock_get_hooks):
        mock_get_hooks.return_value = [lambda: [SkillSetFilter], lambda: [AssetsFilter]]
        cache = HookCache()
        hooks = cache.get_hooks()
        self.assertEqual(len(hooks), 2)
        self.assertTrue(SkillSetFilter in hooks)
        self.assertTrue(AssetsFilter in hooks)
        # Test caching
        hooks_again = cache.get_hooks()
        self.assertEqual(hooks, hooks_again)
        mock_get_hooks.assert_called_once()

    @patch("squads.signals.hooks.get_hooks")
    def test_ignores_duplicate_hooks(self, mock_get_hooks):
        # Mock get_hooks, um zweimal dasselbe Filtermodell zurückzugeben
        mock_get_hooks.return_value = [
            lambda: [SkillSetFilter],
            lambda: [SkillSetFilter],
        ]
        cache = HookCache()
        hooks = cache.get_hooks()
        # Erwarten, dass trotz des Versuchs, dasselbe Modell zweimal hinzuzufügen,
        # es nur einmal in der Liste erscheint
        self.assertEqual(len(hooks), 1)
        self.assertTrue(SkillSetFilter in hooks)


class TestNewFilterSignal(TestCase):
    @patch("squads.signals.model.SquadFilter.objects.create")
    def test_new_filter_created(self, mock_create):
        mock_instance = MagicMock()
        new_filter(sender=None, instance=mock_instance, created=True)
        mock_create.assert_called_once_with(filter_object=mock_instance)

    @patch("squads.signals.model.SquadFilter.objects.create")
    def test_new_filter_not_created(self, mock_create):
        mock_instance = MagicMock()
        new_filter(sender=None, instance=mock_instance, created=False)
        mock_create.assert_not_called()

    @patch("squads.signals.logger.error")
    def test_exception_logging(self, mock_logger):
        new_filter(sender=None, instance=None, created=True)
        mock_logger.assert_called_once()


class TestRemoveFilterSignal(TestCase):
    @patch("squads.signals.model.SquadFilter.objects.get")
    def test_remove_filter(self, mock_get):
        mock_instance = MagicMock()
        mock_instance.pk = 1
        mock_instance.__class__.__name__ = "TestModel"
        mock_filter = MagicMock()
        mock_get.return_value = mock_filter
        rem_filter(sender=None, instance=mock_instance)
        mock_get.assert_called_once()
        mock_filter.delete.assert_called_once()

    @patch("squads.signals.logger.error")
    @patch("squads.signals.model.SquadFilter.objects.get")
    def test_exception_logging(self, mock_get, mock_logger):
        mock_filter = MagicMock()
        mock_get.return_value = mock_filter
        rem_filter(sender=None, instance=None)
        mock_logger.assert_called_once()
