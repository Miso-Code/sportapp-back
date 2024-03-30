resource "aws_iam_role" "function_role" {
  name = "${var.function_name}-role"

  assume_role_policy = jsonencode({
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_lambda_function" "function" {
  function_name = var.function_name
  timeout       = 5 # seconds
  image_uri     = var.image_uri
  package_type  = "Image"

  role = aws_iam_role.function_role.arn

  environment {
    variables = var.environment_variables
  }
}
