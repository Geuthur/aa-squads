from ninja import NinjaAPI
from ninja.security import django_auth

from django.conf import settings

from squads.api import groups
from squads.hooks import get_extension_logger

logger = get_extension_logger(__name__)

api = NinjaAPI(
    title="Squads API",
    version="0.1.0",
    urls_namespace="squads:new_api",
    auth=django_auth,
    csrf=True,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)

# Add the character endpoints
groups.setup(api)
