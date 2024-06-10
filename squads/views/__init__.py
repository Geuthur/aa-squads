"""
View
"""

from .application import apply_group, leave_group
from .groups import broswe_groups, create_group, view_group
from .main import squads_index, squads_membership, squads_pending
from .manage import (
    delete_group,
    delete_membership,
    edit_group,
    manage_application_accept,
    manage_application_decline,
    manage_groups,
    manage_members,
    manage_pendings,
)
