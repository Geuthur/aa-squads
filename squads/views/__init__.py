"""
View
"""

from .application import apply_group, leave_group
from .groups import broswe_groups, view_group
from .main import squads_index, squads_membership, squads_pending
from .manage import (
    accept_group,
    create_group,
    decline_group,
    delete_group,
    delete_membership,
    edit_group,
    manage_groups,
    manage_members,
    manage_pendings,
)
