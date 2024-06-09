"""Admin models"""

from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from squads.models.skills import GroupSkillFilter, SkillSetFilter


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


@admin.register(GroupSkillFilter)
class GroupFilterAdmin(admin.ModelAdmin):
    filter_horizontal = ["skill_filters"]
    list_display = ["__str__", "enabled"]
