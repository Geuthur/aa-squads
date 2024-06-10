"""Hook into Alliance Auth"""

# Django
# Alliance Auth
from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from squads import app_settings, urls
from squads.hooks import get_extension_logger
from squads.models.filters import AssetsFilter, ShipFilter, SkillSetFilter

logger = get_extension_logger(__name__)


class SquadsMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        super().__init__(
            f"{app_settings.SQUADS_APP_NAME}",
            "fa-solid fa-users-between-lines",
            "squads:index",
            navactive=["squads:"],
        )

    def render(self, request):
        if request.user.has_perm("squads.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """Register the menu item"""

    return SquadsMenuItem()


@hooks.register("url_hook")
def register_urls():
    """Register app urls"""

    return UrlHook(urls, "squads", r"^squads/")


@hooks.register("squads_filters")
def filters():
    return [SkillSetFilter, AssetsFilter, ShipFilter]
