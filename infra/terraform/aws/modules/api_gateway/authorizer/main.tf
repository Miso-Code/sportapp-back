data "aws_iam_policy_document" "invocation_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "invocation_role" {
  name               = "api_gateway_auth_invocation"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.invocation_assume_role.json
}

data "aws_iam_policy_document" "invocation_policy" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.lambda_authorizer_arn]
  }
}

resource "aws_iam_role_policy" "invocation_policy" {
  name   = "default"
  role   = aws_iam_role.invocation_role.id
  policy = data.aws_iam_policy_document.invocation_policy.json
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.authorizer_name}-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_lambda_function" "function" {
  function_name = "${var.authorizer_name}-function"
  timeout       = 5 # seconds
  image_uri     = "887664210442.dkr.ecr.us-east-1.amazonaws.com/lambda_authorizer:latest"
  package_type  = "Image"

  role = aws_iam_role.lambda.arn

  environment {
    SECRET_NAME = "LABDA_AUTHORIZER_SECRET"
  }
}

resource "aws_api_gateway_authorizer" "authorizer" {
  name                   = var.authorizer_name
  rest_api_id            = var.api_gateway_id
  authorizer_uri         = aws_lambda_function.function.invoke_arn
  authorizer_credentials = aws_iam_role.invocation_role.arn
}