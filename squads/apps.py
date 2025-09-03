"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Squads
from squads import __version__


# pylint: disable=unused-import, import-outside-toplevel
class SquadsConfig(AppConfig):
    """App Config"""

    default_auto_field = "django.db.models.AutoField"
    author = "Geuthur"
    name = "squads"
    label = "squads"
    verbose_name = f"Squads v{__version__}"

    def ready(self):
        # AA Squads
        import squads.signals
