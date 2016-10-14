from mongoengine.connection import get_connection
import mongomock


def test_adapter(adapter):
    assert adapter.mongodb_name == 'test'

# def test_connect_app(client, app_obj):
#     database = 'mongotest'
#     client.connect_to_database(
#         database='mongotest',
#         host='mongomock://localhost',
#         port=27019,
#         username=None,
#         password=None
#     )
#     assert client.mongodb_name == database