from squads.models.groups import Groups
from squads.models.member import Pending


def add_info_to_context(request, context: dict) -> dict:
    """Add additional information to the context for the view."""
    pending_count = Pending.objects.filter(user=request.user).count()
    new_context = {
        **{
            "pending_count": pending_count,
        },
        **context,
    }
    return new_context


def check_permission(request, group: Groups):
    """Check if the user has the permission."""
    visible = Groups.objects.visible_to(request.user)
    if group not in visible:
        return False
    return True
