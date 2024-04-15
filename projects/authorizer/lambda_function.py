# A simple token-based authorizer example to demonstrate how to use an authorization token
# to allow or deny a request. In this example, the caller named 'user' is allowed to invoke
# a request if the client-supplied token value is 'allow'. The caller is not allowed to invoke
# the request if the token value is 'deny'. If the token value is 'unauthorized' or an empty
# string, the authorizer function returns an HTTP 401 status code. For any other token value,
# the authorizer returns an HTTP 500 status code.
# Note that token values are case-sensitive.

import json
import jwt
import os
import boto3

client = boto3.client("secretsmanager")


def lambda_handler(event, context):
    response = {"isAuthorized": False, "context": {}}

    try:
        secret = _get_secret(os.environ.get("SECRET_NAME", "test"))
        token = event.get("headers", {}).get("authorization", "").split(" ")[-1]
        payload = _get_token_payload(token, secret)
        is_authorized = False
        if "scopes" in payload:
            scopes = payload["scopes"]
            is_authorized = bool(os.environ.get("AUTH_SCOPE", "") in scopes)
            response["context"] = {"user_id": payload.get("user_id", "")}
        response["isAuthorized"] = is_authorized

        return response
    except BaseException as e:
        print("denied:", e)
        return response


def _get_token_payload(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception as e:
        raise Exception("Unauthorized", e)


def _get_secret(secret_name):
    if secret_name == "test":
        return "secretToken"

    client_response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(client_response["SecretString"]).get(secret_name)

    return secret
