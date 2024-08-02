PROFILE_FIELDS = ("phone", "telegram", "bio", "birthday", "time_zone")
USER_FIELDS = (
    "email",
    "first_name",
    "last_name",
    "middle_name",
    "image",
    "profile",
)
USER_DATA = {
    "email": "fake1@fake.com",
    "password": "randomPassword12363",
}


def check_user_response(json_response):
    for field in USER_FIELDS:
        assert field in json_response
    assert len(USER_FIELDS) == len(json_response)

    profile_response = json_response["profile"]
    for field in PROFILE_FIELDS:
        assert field in profile_response
    assert len(PROFILE_FIELDS) == len(profile_response)


def check_patch_me(json_response, new_data):
    for field in USER_FIELDS:
        if field in new_data:
            assert new_data[field] == json_response[field]

    profile_response = json_response["profile"]
    for field in PROFILE_FIELDS:
        if field in new_data:
            assert new_data[field] == profile_response[field]
