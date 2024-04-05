import unittest
from unittest.mock import MagicMock, patch

import lambda_function
import jwt
import uuid


def _generate_event():
    return {"headers": {"authorization": "Bearer " + jwt.encode({"scopes": ["test"], "user_id": str(uuid.uuid4())}, "secretToken", algorithm="HS256")}}


@patch("lambda_function.client")
def test_handler_should_work_with_valid_token(mock_boto3_client):
    event = _generate_event()
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == True
    assert "user_id" in response["context"]


@patch("lambda_function.client")
def test_handler_should_work_with_invalid_token(mock_boto3_client):
    event = _generate_event()
    event["headers"]["authorization"] = "Bearer invalid_token"
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == False


@patch("lambda_function.client")
def test_handler_should_work_with_invalid_header(mock_boto3_client):
    event = _generate_event()
    event["headers"]["authorization"] = "invalid_header_value"
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == False


@patch("lambda_function.client")
def test_handler_should_work_with_no_header(mock_boto3_client):
    event = _generate_event()
    event["headers"] = {}
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == False


@patch("lambda_function.client")
def test_handler_should_work_with_invalid_scope(mock_boto3_client):
    event = _generate_event()
    event["headers"]["authorization"] = "Bearer " + jwt.encode({"scope": "invalid", "user_id": str(uuid.uuid4())}, "secretToken", algorithm="HS256")
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == False
    assert "user_id" in response["context"]


@patch("lambda_function.client")
def test_handler_should_work_with_no_token(mock_boto3_client):
    event = {}
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == False


@patch("lambda_function.client")
def test_handler_should_work_with_invalid_secret(mock_boto3_client):
    event = _generate_event()
    event["headers"]["authorization"] = "Bearer " + jwt.encode({"scope": "invalid", "user_id": str(uuid.uuid4())}, "invalid_secret", algorithm="HS256")
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == False


@patch("lambda_function.client")
def test_handler_should_work_with_expired_token(mock_boto3_client):
    event = _generate_event()
    event["headers"]["authorization"] = "Bearer " + jwt.encode(
        {"scope": "test", "user_id": str(uuid.uuid4()), "exp": 0},
        "secretToken",
        algorithm="HS256",
    )
    context = {}
    response = lambda_function.lambda_handler(event, context)
    assert response["isAuthorized"] == False


@patch("lambda_function.client")
def test_handler_get_secret_should_return_secret(mock_boto3_client):
    mock_boto3_client.get_secret_value.return_value = {"SecretString": '{"get": "super_secret_stuff"}'}
    secret = lambda_function._get_secret("get")
    assert secret == "super_secret_stuff"
