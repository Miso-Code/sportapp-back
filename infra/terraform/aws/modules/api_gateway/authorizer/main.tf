resource "aws_lambda_function" "function" {
  function_name = "${var.authorizer_name}-function"
  timeout = 3 # seconds
  image_uri     = "887664210442.dkr.ecr.us-east-1.amazonaws.com/authorizer:latest"
  package_type  = "Image"

  role = var.lambda_role_arn

  environment {
    variables = {
      SECRET_NAME = "JWT_SECRET"
      AUTH_SCOPE  = var.authorizer_scope
    }
  }
}
