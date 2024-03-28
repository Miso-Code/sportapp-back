import uuid

import main
import jwt
import os
import uuid

os.environ["AUTH_SCOPE"] = "test"


def _generate_event():
    return {
        "headers": {
            "Authorization": "Bearer " + jwt.encode({
                "scope": "test", "user_id": str(uuid.uuid4())
            }, 'secretToken',
                algorithm='HS256')
        }
    }


def test_handler_should_work_with_valid_token():
    event = _generate_event()
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == True
    assert "payload" in response["context"]

def test_handler_should_work_with_invalid_token():
    event = _generate_event()
    event["headers"]["Authorization"] = "Bearer invalid_token"
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == False

def test_handler_should_work_with_invalid_header():
    event = _generate_event()
    event["headers"]["Authorization"] = "invalid_header_value"
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == False

def test_handler_should_work_with_no_header():
    event = _generate_event()
    event["headers"] = {}
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == False

def test_handler_should_work_with_invalid_scope():
    event = _generate_event()
    event["headers"]["Authorization"] = "Bearer " + jwt.encode({
        "scope": "invalid", "user_id": str(uuid.uuid4())
    }, 'secretToken',
        algorithm='HS256')
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == False
    assert "payload" in response["context"]

def test_handler_should_work_with_no_token():
    event = {}
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == False

def test_handler_should_work_with_invalid_secret():
    event = _generate_event()
    event["headers"]["Authorization"] = "Bearer " + jwt.encode({
        "scope": "invalid", "user_id": str(uuid.uuid4())
    }, 'invalid_secret',
        algorithm='HS256')
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == False

def test_handler_should_work_with_expired_token():
    event = _generate_event()
    event["headers"]["Authorization"] = "Bearer " + jwt.encode({
        "scope": "test", "user_id": str(uuid.uuid4()),
        "exp": 0
    }, 'secretToken',
        algorithm='HS256', )
    context = {}
    response = main.handler(event, context)
    assert response["isAuthorized"] == False
