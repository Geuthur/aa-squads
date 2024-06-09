"""Groups views."""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render

from squads.forms import CommentForm
from squads.hooks import get_extension_logger
from squads.models.filters import SquadGroup
from squads.models.groups import Groups, Pending
from squads.models.memberships import Memberships
from squads.views._core import add_info_to_context

logger = get_extension_logger(__name__)


@login_required
@permission_required("squads.basic_access")
def broswe_groups(request):
    groups_list = Groups.objects.all()
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

    skill_req = True
    if filters:
        # Check all Filters
        skill_req = filters.check_user(request.user)

    if request.method == "POST" and "join_group" in request.POST:
        return redirect("squads:view_group", group_id=group_id)

    context = {
        "group": group,
        "comment_form": comment_form,
        "pending_application": pending_application,
        "membership": membership,
        "skill_req": skill_req,
    }

    return render(
        request, "squads/groups/view_group.html", add_info_to_context(request, context)
    )
