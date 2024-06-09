"""
Manager for the Squad model.
"""

from django.db import models

from squads.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class GroupsQuerySet(models.QuerySet):
    def visible_to(self, user):
        # superusers get all visible
        if user.is_superuser:
            logger.debug("Returning all Squads for superuser %s.", user)
            return self

        if user.has_perm("squads.squad_admin"):
            logger.debug("Returning all Squads for Squad Admin %s.", user)
            return self

        if user.has_perm("squads.squad_manager"):
            query = models.Q(owner=user)
            logger.debug("Returning own Squads for %s.", user)
            return self.filter(query)
        return self.none()


class GroupsManager(models.Manager):
    def get_queryset(self):
        return GroupsQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)
