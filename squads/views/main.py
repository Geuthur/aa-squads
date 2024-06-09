# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from squads.models.groups import Pending
from squads.models.memberships import Memberships
from squads.views._core import add_info_to_context


@login_required
@permission_required("squads.basic_access")
def squads_index(request):

    context = {}

    return render(request, "squads/index.html", add_info_to_context(request, context))


@login_required
@permission_required("squads.basic_access")
def squads_membership(request):
    memberships = Memberships.objects.filter(user=request.user)

    context = {"memberships": memberships}

    return render(
        request,
        "squads/groups/membership_groups.html",
        add_info_to_context(request, context),
    )


@login_required
@permission_required("squads.basic_access")
def squads_pending(request):
    pending_memberships = Pending.objects.filter(user=request.user, approved=False)

    context = {"pending_memberships": pending_memberships}

    return render(
        request,
        "squads/groups/pending_groups.html",
        add_info_to_context(request, context),
    )
