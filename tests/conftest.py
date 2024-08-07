# flake8: noqa: E501
import random
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.projects.models import Department, Member, Project, Team
from apps.users.models import Profile

TAGS_COUNT = 3
CITIES = ["City1", "City2", "City3"]
POSITIONS = ["Position1", "Position2", "Position3", "Position4"]


@pytest.fixture
def password():
    return "Qwwte7435ge!erty123"


@pytest.fixture
def admin_user(django_user_model, password):
    user_data = {
        "email": "admin@example.com",
        "password": password,
        "first_name": "admin",
    }
    return django_user_model.objects.create_superuser(**user_data)


@pytest.fixture
def user(django_user_model, password):
    user_data = {
        "email": "user@example.com",
        "password": password,
        "first_name": "first_name",
        "last_name": "last_name",
        "middle_name": "middle_name",
    }
    return django_user_model.objects.create_user(**user_data)


@pytest.fixture
def user_with_profile(user):
    profile = user.profile
    profile.position = "Инженер"
    profile.city = "City1"
    profile.save()
    return user


def client_force(user):
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def admin_client(admin_user):
    return client_force(admin_user)


@pytest.fixture
def user_client(user):
    return client_force(user)


@pytest.fixture
def test_project(admin_user):
    return Project.objects.create(
        owner=admin_user,
        name="test_project",
        description="Description",
        started=timezone.now().date(),
        ended=timezone.now().date(),
    )


@pytest.fixture
def create_projects(create_users):
    return Project.objects.bulk_create(
        [
            Project(
                name=f"test_{i+1}",
                started=timezone.now() + timedelta(days=random.randint(1, 14)),
                ended=timezone.now()
                + timedelta(
                    days=random.randint(100, 140),
                ),
                owner=random.choice(create_users),
            )
            for i in range(20)
        ]
    )


@pytest.fixture
def create_users(django_user_model, password):
    users = django_user_model.objects.bulk_create(
        [
            django_user_model(
                email=f"user_{i+1}@example.com",
                password=password,
            )
            for i in range(15)
        ]
    )
    Profile.objects.bulk_create([Profile(user=u) for u in users])

    return users


@pytest.fixture
def test_departments():
    return Department.objects.bulk_create(
        [Department(name=f"Department {i+1}") for i in range(5)]
    )


@pytest.fixture
def test_team(admin_user, test_departments):
    team = Team.objects.create(
        name="test_team", description="description", owner=admin_user
    )
    Member.objects.create(team=team, user=admin_user, department_id=1)
    return team


@pytest.fixture
def test_teams(create_users, test_departments):
    return Team.objects.bulk_create(
        Team(owner=random.choice(create_users), name=f"Team {i+1}")
        for i in range(10)
    )


@pytest.fixture
def test_members(test_teams, create_users, test_departments):
    return Member.objects.bulk_create(
        [
            Member(
                team_id=i + 1,
                user=random.choice(create_users),
                department=random.choice(test_departments),
            )
            for i in range(10)
        ]
    )


@pytest.fixture
def test_member(test_teams, test_departments, user_with_profile):
    return Member.objects.create(
        team=random.choice(test_teams),
        user=user_with_profile,
        department=random.choice(test_departments),
    )


@pytest.fixture
def test_members_with_profile(test_members):
    c = len(CITIES)
    p = len(POSITIONS)
    for i, member in enumerate(test_members):
        profile = member.user.profile
        profile.city = CITIES[i % c]
        profile.position = POSITIONS[i % p]
        profile.save()
    return test_members
