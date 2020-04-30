from scout.build.user import build_user


def test_delete_user(adapter):
    institutes = ["test-1", "test-2"]
    ## GIVEN an adapter with two users
    for i, ins in enumerate(institutes, 1):
        user_info = {
            "email": "clark.kent{}@mail.com".format(i),
            "id": "clke0" + str(i),
            "location": "here",
            "name": "Clark Kent",
            "institutes": [ins],
        }
        user_obj = build_user(user_info)
        user_obj = adapter.add_user(user_obj)
    assert sum(1 for user in adapter.users()) == 2
    ## WHEN deleting a user
    adapter.delete_user(email="clark.kent1@mail.com")

    ## THEN assert that there is only ine user left
    assert sum(1 for user in adapter.users()) == 1


def test_update_user(real_adapter):
    adapter = real_adapter
    ## GIVEN an adapter with a user
    user_info = {
        "email": "clark.kent@mail.com",
        "location": "here",
        "name": "Clark Kent",
        "institutes": ["test-1"],
    }
    user_obj = build_user(user_info)
    user_obj = adapter.add_user(user_obj)
    assert user_obj["institutes"] == ["test-1"]
    ## WHEN updating a user
    user_info["institutes"].append("test-2")
    user_obj = build_user(user_info)

    adapter.update_user(user_obj)
    ## THEN assert that the user is in the database
    updated_user = adapter.user_collection.find_one()
    assert set(updated_user["institutes"]) == set(["test-1", "test-2"])


def test_insert_user(adapter):
    user_info = {
        "email": "clark.kent@mail.com",
        "location": "here",
        "name": "Clark Kent",
        "institutes": ["test-1"],
    }
    user_obj = build_user(user_info)
    ## GIVEN a empty adapter

    assert adapter.user_collection.find_one() is None

    ## WHEN inserting a user
    user_obj = adapter.add_user(user_obj)

    ## THEN assert that the user is in the database
    assert adapter.user_collection.find_one()


def test_get_users_institute(adapter):
    institutes = ["test-1", "test-2"]
    ## GIVEN an adapter with multiple users
    for i, ins in enumerate(institutes, 1):
        user_info = {
            "email": "clark.kent{}@mail.com".format(i),
            "id": "clke0" + str(i),
            "location": "here",
            "name": "Clark Kent",
            "institutes": [ins],
        }
        user_obj = build_user(user_info)
        user_obj = adapter.add_user(user_obj)
    ## WHEN fetching all users
    users = adapter.users(institute=institutes[0])

    ## THEN assert that both users are fetched
    assert sum(1 for user in users) == 1


def test_get_users(adapter):
    institutes = ["test-1", "test-2"]
    ## GIVEN an adapter with multiple users
    for i, ins in enumerate(institutes, 1):
        user_info = {
            "email": "clark.kent{}@mail.com".format(i),
            "id": "clke0" + str(i),
            "location": "here",
            "name": "Clark Kent",
            "institutes": [ins],
        }
        user_obj = build_user(user_info)
        user_obj = adapter.add_user(user_obj)
    ## WHEN fetching all users
    users = adapter.users()

    ## THEN assert that both users are fetched
    assert sum(1 for user in users) == len(institutes)


def test_get_user_id(adapter):
    user_info = {
        "email": "clark.kent@mail.com",
        "id": "clke01",
        "location": "here",
        "name": "Clark Kent",
        "institutes": ["test-1"],
    }
    user_obj = build_user(user_info)
    user_obj = adapter.add_user(user_obj)
    ## WHEN fetching the user with email
    user = adapter.user(user_id="clke01")

    ## THEN assert that the user is fetched
    assert user


def test_get_user_email(adapter):
    user_info = {
        "email": "clark.kent@mail.com",
        "id": "clke01",
        "location": "here",
        "name": "Clark Kent",
        "institutes": ["test-1"],
    }
    user_obj = build_user(user_info)
    user_obj = adapter.add_user(user_obj)
    ## WHEN fetching the user with email
    user = adapter.user(email="clark.kent@mail.com")

    ## THEN assert that the user is fetched
    assert user


def test_get_nonexisting_user(adapter):
    ## GIVEN an empty adapter
    assert adapter.user_collection.find_one() is None
    ## WHEN fetching a non existing user
    user_obj = adapter.user(email="john.doe@mail.com")
    ## THEN assert the user is None
    assert user_obj is None
