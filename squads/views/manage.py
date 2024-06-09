"""Manage views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe

from squads.forms import SquadsGroupForm
from squads.hooks import get_extension_logger
from squads.models.groups import Groups, Pending
from squads.models.memberships import Memberships

logger = get_extension_logger(__name__)


@login_required
@transaction.atomic
def create_group(request):
    if request.method == "POST":
        form = SquadsGroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.description = mark_safe(group.description)
            if not group.image:  # Überprüfen, ob das Bildfeld leer ist
                group.image = "squads/groups_images/empty.png"  # Standardbild setzen
            group.owner = request.user
            group.save()  # Save the group to the database before creating related Skills
            messages.success(request, "Group has been created.")
            return redirect("squads:groups")
    else:
        form = SquadsGroupForm()
    return render(request, "squads/manage/create_group.html", {"form": form})


@login_required
@transaction.atomic
def accept_group(request, application_id):
    pending = get_object_or_404(Pending, application_id=application_id)
    if pending:
        Memberships.objects.create(
            group=pending.group,
            user=pending.user,
            has_required_skills=True,
            is_active=True,
        )
        Pending.objects.filter(application_id=application_id).delete()
        messages.success(request, f"{pending.user.username} has been approved.")
    else:
        messages.error(request, "%s does not exist.", application_id)

    return redirect("squads:manage_pendings")


@login_required
@transaction.atomic
def decline_group(request, application_id):
    pending = get_object_or_404(Pending, application_id=application_id)
    if pending:
        Pending.objects.filter(application_id=application_id).delete()
        messages.success(request, f"{pending.user.username} has been declined.")
    else:
        messages.error(request, f"{application_id} does not exist.")

    return redirect("squads:manage_pendings")


@login_required
def manage_pendings(request):
    manage_memberships = Groups.objects.filter(owner=request.user)
    return render(
        request,
        "squads/manage/manage_pendings.html",
        {"manage_memberships": manage_memberships},
    )


@login_required
def manage_members(request):
    manage_memberships = Memberships.objects.filter(user=request.user)
    return render(
        request,
        "squads/manage/manage_members.html",
        {"manage_memberships": manage_memberships},
    )


@login_required
def delete_membership(request, application_id):
    membership = get_object_or_404(Memberships, application_id=application_id)
    if membership:
        Memberships.objects.filter(application_id=application_id).delete()
        messages.success(request, f"{membership.user.username} has been removed.")
    else:
        messages.error(request, f"{application_id} does not exist.")

    return redirect("squads:manage_members")


@login_required
def manage_groups(request):
    manage_squads = Groups.objects.filter(owner=request.user)
    return render(
        request,
        "squads/manage/manage_squads.html",
        {"manage_squads": manage_squads},
    )


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Groups, pk=group_id)
    if group:
        Groups.objects.filter(pk=group_id).delete()
        messages.success(request, f"{group.name} has been removed.")
    else:
        messages.error(request, f"{group_id} does not exist.")

    return redirect("squads:manage_groups")


@login_required
def edit_group(request, group_id):
    group_data = get_object_or_404(Groups, pk=group_id)
    if request.method == "POST":
        form = SquadsGroupForm(request.POST, request.FILES, instance=group_data)
        if form.is_valid():
            group = form.save(commit=False)
            group.description = mark_safe(group.description)
            if not group.image:
                group.image = "squads/groups_images/empty.png"
            group.save()
            messages.success(request, f"{group_data.name} has been updated.")
            return redirect("squads:manage_groups")
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
