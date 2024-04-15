"""
This is an example of a lambda function that can be used as a target for api gateway
This is not intended to be deployed but to be used as a reference for the authorizer development
"""

import json
import ast


def object_2_dict(context):
    def set_val(val):
        if type(val) in [str, int, bool, list, dict]:
            return val
        return object_2_dict(val)

    return {attr: set_val(getattr(context, attr)) for attr in dir(context) if not attr.startswith("__") and not callable(getattr(context, attr))}


def handler(event, context):
    print("RECEIVED EVENT", event)
    return {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"context": object_2_dict(context), "event": ast.literal_eval(str(event))}),
    }
