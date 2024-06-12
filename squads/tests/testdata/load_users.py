"""Generate AllianceAuth test objects from allianceauth.json."""

import json
from pathlib import Path

from django.contrib.auth.models import User

from squads.models.groups import Groups


def load_users():
    User.objects.all().delete()

    User.objects.create_user(username="groupuser", password="testpassword1")
    User.objects.create_user(username="groupuser2", password="testpassword2")
    User.objects.create_user(
        username="groupuser3", password="testpassword3", is_staff=True
    )
    User.objects.create_user(
        username="groupuser4", password="testpassword4", is_superuser=True
    )
