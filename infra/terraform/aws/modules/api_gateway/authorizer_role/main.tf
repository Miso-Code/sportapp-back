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

data "aws_iam_policy" "basic_lambda_execution" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "lambda_get_secrets_role" {
  name               = "lambda-authorizer-role${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = data.aws_iam_policy.basic_lambda_execution.arn
  role       = aws_iam_role.lambda_get_secrets_role.name
}

resource "aws_iam_role_policy" "secretmanager_policy" {
  name = "lambda-secretmanager-policy${var.environment}"
  role = aws_iam_role.lambda_get_secrets_role.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "secretsmanager:GetSecretValue",
        "Resource": "*"
    }]
}
EOF
}
