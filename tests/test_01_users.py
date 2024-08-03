from rest_framework import status
from tests.utils import USER_DATA, check_patch_me, check_user_response

url_users = "/api/v1/users/"
url_user_by_id = "/api/v1/users/{id}/"
url_me = "/api/v1/users/me/"
url_avatar = "/api/v1/users/avatar/"


def test_admin_create_user(admin_client):
    response = admin_client.post(
        url_users,
        data=USER_DATA,
    )
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    fields = ("email",)
    for field in fields:
        assert field in json_response
    assert len(fields) == len(json_response)


def test_user_cannot_create_user(user_client):
    response = user_client.post(url_users, data=USER_DATA)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_me(user_client):
    response = user_client.get(url_me)
    assert response.status_code == status.HTTP_200_OK

    check_user_response(response.json())


def test_patch_me(user_client):
    new_data = {"telegram": "@new_telegram", "bio": "About me."}
    response = user_client.patch(url_me, data=new_data)
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()
    check_user_response(json_response)
    check_patch_me(json_response, new_data)


def test_get_user(user_client, admin_user):
    response = user_client.get(url_user_by_id.format(id=admin_user.id))
    assert response.status_code == status.HTTP_200_OK

    check_user_response(response.json())


def test_anonymous_user(client, user):
    response = client.post(url_users, data=USER_DATA)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(url_me)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(url_me, data={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(url_user_by_id.format(id=user.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_user_avatar(user_client, user):
    response = user_client.patch(
        url_avatar,
        data={
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
        },
    )
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.image is not None
