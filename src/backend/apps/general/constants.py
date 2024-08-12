from dataclasses import dataclass


@dataclass(frozen=True)
class CacheKey:
    POSITIONS = "positions"
    CITIES = "cities"
    TEAMS = "teams"
    TEAM_BY_ID = "team:%d"
    MEMBERS = "members"
    MEMBERS_TEAM_BY_ID = "members:team:%d"
    DEPARTMENTS = "departments"
