"""Admin models"""

from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from squads.models.filters import AssetsFilter, SkillSetFilter, SquadFilter, SquadGroup


@admin.register(SkillSetFilter)
class SkillSetFilterAdmin(admin.ModelAdmin):
    """
    SkillSetFilterAdmin
    """

    list_display = ("description", "_skill_sets")
    filter_horizontal = ("skill_sets",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)

        return qs.prefetch_related("skill_sets")

    @admin.display()
    def _skill_sets(self, obj) -> str:
        objs = obj.skill_sets.all()

        return ", ".join(sorted([obj.name for obj in objs]))


@admin.register(AssetsFilter)
class AssetsFilterAdmin(admin.ModelAdmin):
    """
    AssetsFilterAdmin
    """

    list_display = ("description", "_assets")
    autocomplete_fields = ["assets"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)

        return qs.prefetch_related("assets")

    @admin.display()
    def _assets(self, obj) -> str:
        objs = obj.assets.all()

        return ", ".join(sorted([obj.name for obj in objs]))


# pylint: disable=unused-argument
@admin.register(SquadFilter)
class SquadFilterAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    list_display = ["__str__"]


@admin.register(SquadGroup)
class SquadGrouprAdmin(admin.ModelAdmin):
    filter_horizontal = ["filters"]
    list_display = ["__str__", "enabled"]
