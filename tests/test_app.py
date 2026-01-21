import pytest
from app import app as flask_app
import json
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('app.redis_client', new_callable=MagicMock)
@patch('app.requests.post')
def test_authorize_success_from_opa(mock_post, mock_redis_client, client):
    # Mock OPA response
    mock_post.return_value.json.return_value = {"result": True}
    mock_post.return_value.status_code = 200

    # Mock Redis client
    mock_redis_client.get.return_value = None
    mock_redis_client.setex.return_value = True

    # Make request
    response = client.post('/authorize',
                           data=json.dumps({'user': 'test', 'action': 'read', 'resource': 'data'}),
                           content_type='application/json')

    # Assertions
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] is True
    assert data['source'] == 'OPA'

@patch('app.redis_client', new_callable=MagicMock)
def test_authorize_success_from_cache(mock_redis_client, client):
    # Mock Redis client
    mock_redis_client.get.return_value = json.dumps(True)

    # Make request
    response = client.post('/authorize',
                           data=json.dumps({'user': 'test', 'action': 'read', 'resource': 'data'}),
                           content_type='application/json')

    # Assertions
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] is True
    assert data['source'] == 'Redis Cache'
