"""Manage views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect

from squads.forms import CommentForm
from squads.hooks import get_extension_logger
from squads.models.groups import Groups, Pending
from squads.models.memberships import Memberships

logger = get_extension_logger(__name__)


@login_required
@permission_required("squads.basic_access")
def apply_group(request, group_id):
    group = get_object_or_404(Groups, id=group_id)
    comment_form = CommentForm(request.POST or None)

    user_has_required_skills = True

    if user_has_required_skills:
        user = request.user
        comment = None
        if comment_form.is_valid():
            comment = comment_form.cleaned_data.get("comment")
        Pending.objects.create(group=group, user=user, application=comment)
        messages.success(request, "Your application has been submitted.")
    else:
        messages.error(
            request, "You do not meet the skill requirements for this Squad."
        )

    return redirect("squads:view_group", group_id=group_id)


@login_required
@permission_required("squads.basic_access")
def leave_group(request, group_id):
    group = get_object_or_404(Groups, id=group_id)
    membership = Memberships.objects.filter(user=request.user, group=group).first()

    if membership:
        membership.delete()
        messages.success(request, f"You Left {membership.group.name}.")
    else:
        messages.error(request, "You are not in that Squad.")

    return redirect("squads:view_group", group_id=group_id)
