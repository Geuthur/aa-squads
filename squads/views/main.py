# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from squads.models.groups import Pending
from squads.models.memberships import Memberships


@login_required
@permission_required("squads.basic_access")
def squads_index(request):
    return render(request, "squads/index.html")


@login_required
@permission_required("squads.basic_access")
def squads_membership(request):
    memberships = Memberships.objects.filter(user=request.user)
    return render(
        request, "squads/groups/membership_groups.html", {"memberships": memberships}
    )


@login_required
@permission_required("squads.basic_access")
def squads_pending(request):
    pending_memberships = Pending.objects.filter(user=request.user, approved=False)
    return render(
        request,
        "squads/groups/pending_groups.html",
        {"pending_memberships": pending_memberships},
    )
