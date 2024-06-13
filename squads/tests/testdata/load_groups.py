"""Generate AllianceAuth test objects from allianceauth.json."""

import json
import random
from pathlib import Path

from django.contrib.auth.models import User

from squads.models.groups import Groups
from squads.models.member import Memberships, Pending


def load_groups():
    Groups.objects.all().delete()

    Groups.objects.update_or_create(
        id=1,
        name="Group No Approve",
        owner=User.objects.get(username="groupuser"),
        is_active=False,
    )
    Groups.objects.update_or_create(
        id=2,
        name="Group Approve",
        owner=User.objects.get(username="groupuser2"),
        req_approve=True,
    )
    Groups.objects.update_or_create(
        id=3,
        name="Group Staff",
        owner=User.objects.get(username="groupuser3"),
        is_active=False,
        req_approve=True,
    )
    Groups.objects.update_or_create(
        id=4,
        name="Group Superuser",
        owner=User.objects.get(username="groupuser4"),
        is_active=True,
        req_approve=True,
    )


def load_membership():
    Memberships.objects.all().delete()

    group = Groups.objects.get(name="Group No Approve")
    user = User.objects.get(username="groupuser")
    Memberships.objects.create(
        group=group, user=user, req_filters=False, application_id="cf2605fa1ff1"
    )

    group = Groups.objects.get(name="Group Approve")
    user = User.objects.get(username="groupuser2")
    Memberships.objects.create(
        group=group, user=user, req_filters=True, application_id="cf2605fa1ff2"
    )

    group = Groups.objects.get(name="Group Staff")
    user = User.objects.get(username="groupuser3")
    Memberships.objects.create(
        group=group, user=user, req_filters=False, application_id="cf2605fa1ff3"
    )

    group = Groups.objects.get(name="Group Superuser")
    user = User.objects.get(username="groupuser4")
    Memberships.objects.create(
        group=group, user=user, req_filters=True, application_id="cf2605fa1ff4"
    )


def load_pending():
    Pending.objects.all().delete()

    group = Groups.objects.get(name="Group No Approve")
    user = User.objects.get(username="groupuser")
    Pending.objects.create(
        group=group,
        user=user,
        req_filters=False,
        comment="Test Comment",
        application_id="cf2605fa1ff1",
    )

    group = Groups.objects.get(name="Group Approve")
    user = User.objects.get(username="groupuser2")
    Pending.objects.create(
        group=group,
        user=user,
        req_filters=True,
        comment="Test Comment",
        application_id="cf2605fa1ff2",
    )

    group = Groups.objects.get(name="Group Staff")
    user = User.objects.get(username="groupuser3")
    Pending.objects.create(
        group=group, user=user, req_filters=False, application_id="cf2605fa1ff3"
    )

    group = Groups.objects.get(name="Group Superuser")
    user = User.objects.get(username="groupuser4")
    Pending.objects.create(
        group=group, user=user, req_filters=True, application_id="cf2605fa1ff4"
    )
