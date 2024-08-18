PROFILE_FIELDS = (
    "phone",
    "telegram",
    "position",
    "bio",
    "birthday",
    "time_zone",
)
USER_FIELDS = (
    "id",
    "email",
    "full_name",
    "image",
    "profile",
)
USER_PROJECT_FIELDS = USER_FIELDS + ("projects",)
USER_DATA = {
    "email": "fake1@fake.com",
    "password": "randomPassword12363",
}


def check_user_response(json_response, fields=USER_FIELDS):
    errors = [field for field in fields if field not in json_response]
    assert not errors, "Response must contain fields: " + ", ".join(errors)
    assert len(fields) == len(json_response)

    profile_response = json_response["profile"]
    profile_errors = [
        field for field in PROFILE_FIELDS if field not in profile_response
    ]
    assert (
        not profile_errors
    ), "Profile response must contain fields: " + ", ".join(profile_errors)
    assert len(PROFILE_FIELDS) == len(profile_response)


def check_patch_me(json_response, new_data):
    for field in USER_FIELDS:
        if field in new_data:
            assert new_data[field] == json_response[field]

    profile_response = json_response["profile"]
    for field in PROFILE_FIELDS:
        if field in new_data:
            assert new_data[field] == profile_response[field]


API_PREFIX = "/api/v1"
