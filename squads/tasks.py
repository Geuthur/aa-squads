"""App Tasks"""

from celery import chain as Chain
from celery import shared_task

from squads.hooks import get_extension_logger
from squads.models import Groups, Memberships, Pending
from squads.models.filters import SquadGroup

logger = get_extension_logger(__name__)


@shared_task
def run_check_squads(runs: int = 0):
    """Run Check Squads Filters."""
    groups = Groups.objects.filter(is_active=True).all()

    for group in groups:
        logger.debug("Checking group: %s", group.name)
        runs = runs + 1
        Chain(run_check_members.si(group.pk)).delay()
        Chain(run_check_pendings.si(group.pk)).delay()

    logger.info("Check Squads runs completed: %s", runs)


# TODO Maybe delete Member on filter fail??
@shared_task
def run_check_members(group_id: int, runs: int = 0):
    """Run Check Members."""
    group = Groups.objects.get(id=group_id)
    filters = SquadGroup.objects.filter(group=group).first()
    changed_state = 0

    if filters:
        members = Memberships.objects.filter(group=group).all()
        for member in members:
            filter_req, _ = filters.check_user(member.user)
            runs = runs + 1
            if filter_req:
                member.req_filters = True
                member.save()
            else:
                member.req_filters = False
                member.save()
                changed_state += 1
        logger.info(
            "Member Check %s runs completed: %s, Changed: %s",
            group.name,
            runs,
            changed_state,
        )
    return True


# TODO Maybe delete Member on filter fail??
@shared_task
def run_check_pendings(group_id: int, runs: int = 0):
    """Run Check Pendings."""
    group = Groups.objects.get(id=group_id)
    filters = SquadGroup.objects.filter(group=group).first()
    changed_state = 0

    if filters:
        pendings = Pending.objects.filter(group=group).all()
        for pending in pendings:
            filter_req, _ = filters.check_user(pending.user)
            runs = runs + 1
            if filter_req:
                pending.req_filters = True
                pending.save()
            else:
                pending.req_filters = False
                pending.save()
                changed_state += 1
        logger.info(
            "Pending Check %s runs completed: %s, Changed: %s",
            group.name,
            runs,
            changed_state,
        )
    return True
