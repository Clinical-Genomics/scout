
def test_get_insert_user(pymongo_adapter):
    user_info = {
        'email': 'clark.kent@mail.com',
        'location': 'here',
        'name': 'Clark Kent',
        'institutes': ['test-1'],
        
    }

    ## GIVEN a empty adapter
    
    assert pymongo_adapter.user(email=user_info['email']) is None

    ## WHEN insaerting a user
    user_obj = pymongo_adapter.getoradd_user(
        email=user_info['email'],
        name=user_info['name'],
        location=user_info['location'],
        institutes=user_info['institutes'],
    )

    ## THEN assert that the user is in the database
    
    assert user_obj['_id'] == user_info['email']


def test_get_nonexisting_user(pymongo_adapter):
    """docstring for test_get_nonexisting_user"""
    user_obj = pymongo_adapter.user(email='john.doe@mail.com')
    assert user_obj == None
    