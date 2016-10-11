from mongoengine.connection import get_connection
import mongomock


def test_connect(client):
    database = 'mongotest'
    port = 27019
    host = 'mongomock://localhost'
    client.connect_to_database(
        database=database, 
        host=host,
        port=port,
        username=None,
        password=None
    )
    conn = client.get_connection()
    assert isinstance(conn, mongomock.MongoClient)
    assert client.mongodb_name == database
    assert client.port == port
    assert client.host == host

def test_adapter(adapter):
    "Just make sure we are using mongomock"
    conn = adapter.get_connection()
    assert isinstance(conn, mongomock.MongoClient)

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