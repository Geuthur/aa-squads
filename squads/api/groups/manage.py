from typing import List

from ninja import NinjaAPI

from squads.api import schema
from squads.hooks import get_extension_logger
from squads.models.groups import Groups, Pending
from squads.models.memberships import Memberships

logger = get_extension_logger(__name__)


# pylint: disable=duplicate-code
class ManageApiEndpoints:
    tags = ["ManageGroups"]

    def __init__(self, api: NinjaAPI):
        @api.get(
            "groups/{group_id}/pendings/",
            response={200: List[schema.Pending], 403: str},
            tags=self.tags,
        )
        def get_pendings(request, group_id: int):
            groups = Groups.objects.visible_to(request.user)

            group_ids = [group.pk for group in groups]

            if group_id == 0:
                pending_groups = Pending.objects.filter(group__in=group_ids)
            else:
                pending_groups = Pending.objects.filter(group=group_id)

            output = []

            for pending in pending_groups:
                output.append(
                    {
                        "group": pending.group.name,
                        "group_id": pending.group.pk,
                        "user": pending.user.username,
                        "approved": pending.approved,
                        "created_at": pending.created_at,
                        "application": pending.application,
                        "application_id": pending.application_id,
                    }
                )

            return output

        @api.get(
            "groups/{group_id}/members/",
            response={200: List[schema.Members], 403: str},
            tags=self.tags,
        )
        def get_members(request, group_id: int):
            groups = Groups.objects.visible_to(request.user)

            group_ids = [group.pk for group in groups]

            if group_id == 0:
                membership_groups = Memberships.objects.filter(group__in=group_ids)
            else:
                membership_groups = Memberships.objects.filter(group=group_id)

            output = []

            for member in membership_groups:
                output.append(
                    {
                        "group": member.group.name,
                        "group_id": member.group.pk,
                        "user": member.user.username,
                        "has_required_skills": member.has_required_skills,
                        "is_active": member.is_active,
                        "joined_at": member.joined_at,
                        "application_id": member.application_id,
                    }
                )

            return output

        @api.get(
            "groups/{group_id}/",
            response={200: List[schema.Squads], 403: str},
            tags=self.tags,
        )
        def get_squads(request, group_id: int):
            groups = Groups.objects.visible_to(request.user)

            group_ids = [group.pk for group in groups]

            if group_id == 0:
                manage_groups = Groups.objects.filter(pk__in=group_ids)
            else:
                manage_groups = Groups.objects.filter(pk=group_id)

            output = []

            for group in manage_groups:
                output.append(
                    {
                        "group": group.name,
                        "group_id": group.pk,
                        "owner": group.owner.username,
                        "is_active": group.is_active,
                    }
                )

            return output
