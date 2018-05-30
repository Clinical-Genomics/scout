from scout.build.user import build_user


def test_get_insert_user(adapter):
    user_info = {
        'email': 'clark.kent@mail.com',
        'location': 'here',
        'name': 'Clark Kent',
        'institutes': ['test-1'],
        
    }
    user_obj = build_user(user_info)
    ## GIVEN a empty adapter
    
    assert adapter.user(email=user_info['email']) is None

    ## WHEN insaerting a user
    user_obj = adapter.add_user(user_obj)

    ## THEN assert that the user is in the database
    
    assert user_obj['_id'] == user_info['email']


def test_get_nonexisting_user(adapter):
    """docstring for test_get_nonexisting_user"""
    user_obj = adapter.user(email='john.doe@mail.com')
    assert user_obj == None
    