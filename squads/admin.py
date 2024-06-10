"""Admin models"""

from typing import Any

from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from eveuniverse.models import EveGroup

from squads.models.filters import (
    AssetsFilter,
    ShipFilter,
    SkillSetFilter,
    SquadFilter,
    SquadGroup,
)


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


# Create own form for EveGroupFilter
class ShipFilterForm(forms.ModelForm):
    class Meta:
        model = ShipFilter
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ship"].queryset = EveGroup.objects.filter(
            published=1, eve_category__in=[6]
        )


@admin.register(ShipFilter)
class ShippFilterAdmin(admin.ModelAdmin):
    """
    ShipFilterAdmin
    """

    form = ShipFilterForm
    list_display = ("description", "_ship")
    filter_horizontal = ["ship"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)

        return qs.prefetch_related("ship")

    @admin.display()
    def _ship(self, obj) -> str:
        objs = obj.ship.all()

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
