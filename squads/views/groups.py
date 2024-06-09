"""Groups views."""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render

from squads.forms import CommentForm
from squads.hooks import get_extension_logger
from squads.models.groups import Groups, Pending
from squads.models.memberships import Memberships
from squads.models.skills import GroupSkillFilter

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

    return render(request, "squads/groups/browse_groups.html", context)


@login_required
@permission_required("squads.basic_access")
def view_group(request, group_id):
    group = get_object_or_404(Groups, id=group_id)
    comment_form = CommentForm(request.POST or None)
    pending_application = Pending.objects.filter(group=group, user=request.user).first()
    membership = Memberships.objects.filter(user=request.user, group=group).first()

    req_skills = GroupSkillFilter.objects.filter(group=group)
    skill_req = True

    # TODO make a helper function to get missing skills displaying to view
    # Check if any of the required skills are missing
    for skill in req_skills:
        if not any(
            skill_filter.check_skill(request.user)
            for skill_filter in skill.skill_filters.all()
        ):
            skill_req = False
            break
    logger.debug("Skill Req: %s", skill_req)

    if request.method == "POST" and "join_group" in request.POST:
        return redirect("squads:view_group", group_id=group_id)

    return render(
        request,
        "squads/groups/view_group.html",
        {
            "group": group,
            "comment_form": comment_form,
            "pending_application": pending_application,
            "membership": membership,
            "skill_req": skill_req,
        },
    )
