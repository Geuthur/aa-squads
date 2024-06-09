from datetime import datetime
from typing import Optional

from ninja import Schema


class Squads(Schema):
    group: str
    group_id: int
    owner: str
    is_active: bool


class Pending(Schema):
    group: str
    group_id: int
    user: str
    approved: bool
    application: str
    application_id: str
    skills: Optional[str] = None
    created_at: datetime


class Members(Schema):
    group: str
    group_id: int
    user: str
    has_required_skills: bool
    is_active: bool
    joined_at: datetime
    application_id: str
