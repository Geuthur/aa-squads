"""App URLs"""

from django.urls import path, re_path
from django.views.static import serve

from squads.api import api
from squads.views.application import apply_group, leave_group
from squads.views.groups import broswe_groups, view_group
from squads.views.main import squads_index, squads_membership, squads_pending
from squads.views.manage import (
    accept_group,
    create_group,
    decline_group,
    delete_group,
    delete_membership,
    edit_group,
    manage_groups,
    manage_members,
    manage_pendings,
)

app_name: str = "squads"

urlpatterns = [
    # Main
    path("", squads_index, name="index"),
    path("browse", broswe_groups, name="groups"),
    path("create", create_group, name="create_group"),
    # Information
    path("pending", squads_pending, name="pending"),
    path("membership", squads_membership, name="membership"),
    # Manage
    path("accept/<str:application_id>", accept_group, name="accept_group"),
    path("decline/<str:application_id>", decline_group, name="decline_group"),
    path(
        "delete_membership/<str:application_id>",
        delete_membership,
        name="delete_membership",
    ),
    path("delete/<int:group_id>", delete_group, name="delete_group"),
    path("edit/<int:group_id>", edit_group, name="edit_group"),
    path("manage_pendings", manage_pendings, name="manage_pendings"),
    path("manage_members", manage_members, name="manage_members"),
    path("manage_groups", manage_groups, name="manage_groups"),
    # Application
    path("view/<int:group_id>", view_group, name="view_group"),
    path("apply/<int:group_id>", apply_group, name="apply_group"),
    path("leave/<int:group_id>", leave_group, name="leave_group"),
    # API
    re_path(r"^api/", api.urls),
]
urlpatterns += [
    re_path(
        r"^groups_images/(?P<path>.*)$",
        serve,
        {
            "document_root": "squads/groups_images",
        },
    ),
]
