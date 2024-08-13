from dataclasses import dataclass


@dataclass(frozen=True)
class CacheKey:
    PROJECTS = "projects"
    MY_PROJECTS = "my_projects:{user_id}"
    POSITIONS = "positions"
    CITIES = "cities"
    TEAMS = "teams"
    TEAM_BY_ID = "team:{team_id}"
    MEMBERS = "members"
    MEMBERS_TEAM_BY_ID = "members:team:{team_id}"
    DEPARTMENTS = "departments"
