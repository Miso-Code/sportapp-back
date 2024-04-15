
# Authorizer

This project contains an AWS Lambda function that serves as a token-based authorizer for the SportApp. It uses an authorization token to allow or deny requests based on the token's scope.
### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.12 installed
- pip installed

### Setup
Install the necessary Python packages by running
```
pip install -r requirements.txt
```

### Running the Application Locally

You can use the AWS SAM CLI to run the application locally:

1. To build the application, run `sam build -t local_template.yaml`.
2. To start the local API Gateway, run `sam local start-api -t local_template.yaml`.
3. Use Postman or another HTTP client to send requests to the local API Gateway.

This would create an api gateway with the following endpoints:
- `http://localhost:3000/`: an api with `AUTH_SCOPE` set to `SCOPED` that requires a token with the `standard` scope
- `http://localhost:3000/scoped`: an api with `AUTH_SCOPE` set to `SCOPED` that requires a token with the `scoped` scope

The scope is signed as part of the JWT payload, and the authorizer checks for the scope in the token.

Request with a valid token:
```bash
curl --location 'http://127.0.0.1:3000/scoped' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzY29wZSI6InNjb3BlZCIsInVzZXJfaWQiOiIxMjMifQ.VMxYuw8akzk4ezoy5l65f-qwh3rw0aJojfisIBeui1I'
```

### Local Development
During development you may run both commands in different terminals
to see the changes in the code reflected in the local API Gateway.
If the change doesn't modify `local_template.yaml`, you can only re run the `sam build -t local_tempalte.yaml` step.

### Testing

Unit tests are available in the `test_main.py` file. You can run these tests using pytest:

```bash
pytest lambda_function_test.py
```

### Development

To start the development server, run the following command:

### Deployment

This project is intended to be deployed using Terraform, not directly through AWS SAM. However, the `local_template.yaml` file is a valid CloudFormation template and can be used for reference or for local testing with the AWS SAM CLI.

### Environment Variables

The authorizer uses the following environment variables:

- `AUTH_SCOPE`: The scope that the authorizer should check for in the JWT token. We should have 4 different scopes: `BASIC_PLAN`, `INTERMEDIATE_PLAN`, `PREMIUM_PLAN`, and `BUSSINES_PARTNER`. The authorizer will only allow requests with a token that has the specified scope
- `SECRET_NAME`: The name of the AWS Secrets Manager secret that contains the JWT secret key, leave it empty if you want to use the default secret key during development.

### Authorizer Function

The authorizer function is defined in `main.py`. It checks the `Authorization` header of the incoming request for a JWT token. If the token's scope matches the `AUTH_SCOPE` environment variable, the request is authorized.

### Example Function

An example function that can be used as a target for the API Gateway is provided in `local_example.py`. This function simply returns the event and context it receives.
It's being used by `sam local start-api -t local_template.yaml` to test the authorizer function.
