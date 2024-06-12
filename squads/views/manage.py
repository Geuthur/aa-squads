"""Manage views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe

from squads.app_settings import SQUADS_EMPTY_IMAGE
from squads.forms import SquadsGroupForm
from squads.hooks import get_extension_logger
from squads.models.groups import Groups
from squads.models.member import Memberships, Pending
from squads.views._core import check_permission

logger = get_extension_logger(__name__)


# Group Management
@login_required
@permission_required("squads.squad_manager")
@transaction.atomic
def manage_application_accept(request, application_id):
    try:
        pending = Pending.objects.get(application_id=application_id)
    except Pending.DoesNotExist:
        messages.error(request, "%s does not exist.", application_id)
        return redirect("squads:manage_pendings")

    permission = check_permission(request, pending.group)

    if not permission:
        messages.error(
            request, "You do not have permission to accept this application."
        )
        return redirect("squads:manage_pendings")

    Memberships.objects.create(
        group=pending.group,
        user=pending.user,
        req_filters=True,
        is_active=True,
    )
    Pending.objects.filter(application_id=application_id).delete()
    messages.success(request, f"{pending.user.username} has been approved.")
    logger.info("%s has approved %s in %s.", request.user, pending.user, pending.group)
    return redirect("squads:manage_pendings")


@login_required
@permission_required("squads.squad_manager")
def manage_application_decline(request, application_id):
    try:
        pending = Pending.objects.get(application_id=application_id)
    except Pending.DoesNotExist:
        messages.error(request, f"{application_id} does not exist.")
        return redirect("squads:manage_pendings")

    permission = check_permission(request, pending.group)

    if not permission:
        messages.error(
            request, "You do not have permission to decline this application."
        )
        return redirect("squads:manage_pendings")

    Pending.objects.filter(application_id=application_id).delete()
    messages.success(request, f"{pending.user.username} has been declined.")
    logger.info("%s has declined %s in %s.", request.user, pending.user, pending.group)
    return redirect("squads:manage_pendings")


@login_required
@permission_required("squads.squad_manager")
def manage_pendings(request):
    manage_memberships = Groups.objects.filter(owner=request.user)
    return render(
        request,
        "squads/manage/manage_pendings.html",
        {"manage_memberships": manage_memberships},
    )


# Membership Management
@login_required
@permission_required("squads.squad_manager")
def manage_members(request):
    manage_memberships = Memberships.objects.filter(user=request.user)
    return render(
        request,
        "squads/manage/manage_members.html",
        {"manage_memberships": manage_memberships},
    )


@login_required
@permission_required("squads.squad_manager")
def delete_membership(request, application_id):
    try:
        membership = Memberships.objects.get(application_id=application_id)
    except Memberships.DoesNotExist:
        messages.error(request, f"{application_id} does not exist.")
        return redirect("squads:manage_members")

    permission = check_permission(request, membership.group)

    if not permission:
        messages.error(request, "You do not have permission to delete this membership.")
        return redirect("squads:manage_members")

    Memberships.objects.filter(application_id=application_id).delete()
    messages.success(request, f"{membership.user.username} has been removed.")
    logger.info(
        "%s has removed %s from %s.",
        request.user,
        membership.user,
        membership.group,
    )
    return redirect("squads:manage_members")


# Group Management
@login_required
@permission_required("squads.squad_manager")
def manage_groups(request):
    manage_squads = Groups.objects.visible_to(request.user)
    return render(
        request,
        "squads/manage/manage_squads.html",
        {"manage_squads": manage_squads},
    )


@login_required
@permission_required("squads.squad_manager")
def delete_group(request, group_id):
    try:
        group = Groups.objects.get(pk=group_id)
    except Groups.DoesNotExist:
        messages.error(request, f"{group_id} does not exist.")
        return redirect("squads:manage_groups")

    permission = check_permission(request, group)

    if not permission:
        messages.error(request, "You do not have permission to delete this group.")
        return redirect("squads:manage_groups")

    Groups.objects.filter(pk=group_id).delete()
    messages.success(request, f"{group.name} has been removed.")
    logger.info("%s has removed %s.", request.user, group)
    return redirect("squads:manage_groups")


@login_required
@permission_required("squads.squad_manager")
def edit_group(request, group_id):
    try:
        group_data = Groups.objects.get(pk=group_id)
    except Groups.DoesNotExist:
        messages.error(request, f"{group_id} does not exist.")
        return redirect("squads:manage_groups")

    permission = check_permission(request, group_data)

    if not permission:
        messages.error(request, "You do not have permission to edit this group.")
        return redirect("squads:manage_groups")

    if request.method == "POST":
        form = SquadsGroupForm(request.POST, request.FILES, instance=group_data)
        if form.is_valid():
            group_edit = form.save(commit=False)
            group_edit.description = mark_safe(group_edit.description)
            print("valid")
            if not group_edit.image:
                print("no image")
                group_edit.image = SQUADS_EMPTY_IMAGE
            print("saving")
            group_edit.save()
            print("lul")
            messages.success(request, f"{group_data.name} has been updated.")
            return redirect("squads:manage_groups")
        print("invalid")
        messages.error(request, "Something went wrong.")
        return render(
            request,
            "squads/manage/edit_group.html",
            {"form": form, "group": group_data},
        )
    form = SquadsGroupForm(instance=group_data)
    return render(
        request, "squads/manage/edit_group.html", {"form": form, "group": group_data}
    )
