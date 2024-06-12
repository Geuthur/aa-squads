from datetime import datetime

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
    comment: str
    application_id: str
    req_filters: bool
    created_at: datetime


class Members(Schema):
    group: str
    group_id: int
    user: str
    req_filters: bool
    is_active: bool
    joined_at: datetime
    application_id: str
