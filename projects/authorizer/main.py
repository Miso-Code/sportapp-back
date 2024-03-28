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
import requests


def handler(event, context):
    response = {
        "isAuthorized": False,
        "context": {}
    }

    try:
        secret = _get_secret(os.environ.get("SECRET_NAME", "test"))
        token = event.get("headers", {}).get("Authorization", "").split(" ")[-1]
        payload = _get_token_payload(token, secret)
        scope = payload.get("scope", "")
        print("scope: ", scope)
        print("env scope: ", os.environ.get("AUTH_SCOPE", ""))
        response["isAuthorized"] = bool(scope == os.environ.get("AUTH_SCOPE", ""))
        response["context"] = {"payload": payload}

        return response
    except BaseException as e:
        print('denied:', e)
        return response



def _get_token_payload(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except Exception as e:
        raise Exception('Unauthorized')


def _get_secret(secret_name):
    if secret_name == 'test':
        return 'secretToken'
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}

    secrets_extension_http_port = os.environ.get('PARAMETERS_SECRETS_EXTENSION_HTTP_PORT', '2773')

    secrets_extension_endpoint = "http://localhost:" + \
                                 secrets_extension_http_port + \
                                 "/secretsmanager/get?secretId=" + \
                                 secret_name

    r = requests.get(secrets_extension_endpoint, headers=headers)

    secret = json.loads(r.text)[
        "SecretString"]  # load the Secrets Manager response into a Python dictionary, access the secret

    return secret
