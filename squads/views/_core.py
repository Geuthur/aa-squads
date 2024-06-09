from squads.models.groups import Pending


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
