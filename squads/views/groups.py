"""Groups views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe

from squads.app_settings import SQUADS_EMPTY_IMAGE
from squads.forms import CommentForm, SquadsGroupForm
from squads.hooks import get_extension_logger
from squads.models.filters import SquadGroup
from squads.models.groups import Groups, Pending
from squads.models.memberships import Memberships
from squads.views._core import add_info_to_context

logger = get_extension_logger(__name__)


@login_required
@permission_required("squads.squad_manager")
@transaction.atomic
def create_group(request):
    if request.method == "POST":
        form = SquadsGroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.description = mark_safe(group.description)
            if not group.image:
                # Use Static one if empty
                group.image = SQUADS_EMPTY_IMAGE
            group.owner = request.user
            group.save()
            messages.success(request, "Squad has been created.")
            return redirect("squads:groups")
    else:
        form = SquadsGroupForm()
    return render(request, "squads/manage/create_group.html", {"form": form})


@login_required
@permission_required("squads.basic_access")
def broswe_groups(request):
    groups_list = Groups.objects.filter(is_active=True).order_by("name").all()
    membership_ids = Memberships.objects.filter(user=request.user).values_list(
        "group_id", flat=True
    )
    paginator = Paginator(groups_list, 50)

    page = request.GET.get("page")
    try:
        groups = paginator.page(page)
    except PageNotAnInteger:
        groups = paginator.page(1)
    except EmptyPage:
        groups = paginator.page(paginator.num_pages)

    context = {
        "groups": groups,
        "membership_ids": membership_ids,
    }

    return render(
        request,
        "squads/groups/browse_groups.html",
        add_info_to_context(request, context),
    )


@login_required
@permission_required("squads.basic_access")
def view_group(request, group_id):
    group = get_object_or_404(Groups, id=group_id)
    comment_form = CommentForm(request.POST or None)
    pending_application = Pending.objects.filter(group=group, user=request.user).first()
    membership = Memberships.objects.filter(user=request.user, group=group).first()
    filters = SquadGroup.objects.filter(group=group).first()

    filter_req = True
    missing_req = []

    if filters:
        filter_req, missing_req = filters.check_user(request.user)

    context = {
        "group": group,
        "comment_form": comment_form,
        "pending_application": pending_application,
        "membership": membership,
        "filter_req": filter_req,
        "missing_req": missing_req,
    }

    return render(
        request, "squads/groups/view_group.html", add_info_to_context(request, context)
    )
