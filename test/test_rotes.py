from fastapi.testclient import TestClient
from fast_app import app

client = TestClient(app)

def test_index():
    response = client.get("/",
                          headers={
                              'api-key': 'user1'
                          })

    assert response.status_code == 200

def test_profile_me():
    response = client.get("api/users/me",
                          headers={
                              'api-key' : 'user1'
                          })
    assert response.status_code == 200
    assert response.json() == {
        'result': True,
        'user': {
            'id': 1,
            'name': 'pipa',
            'followers': [],
        },
    }

def test_get_tweet():
    response = client.get("api/tweets/1",
                          headers={
                              'api-key' : 'user1'
                          })
    assert response.status_code == 200

def test_post_tweets():
    response = client.get("api/tweets",
                          headers={
                              'api-key': 'user1'
                          },
                          json={'tweet_data': 'Hello'}
)

    assert response.status_code == 201



