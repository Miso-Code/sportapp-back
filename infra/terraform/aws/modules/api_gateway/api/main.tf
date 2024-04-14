resource "aws_apigatewayv2_api" "api" {
  name        = var.api_name
  description = var.api_description

  protocol_type = "HTTP"

  cors_configuration {
    allow_credentials = false
    allow_headers     = [
      "*",
    ]
    allow_methods = [
      "*",
    ]
    allow_origins = [
      "*",
    ]
    expose_headers = [
      "*",
    ]
    max_age = 500
  }
}

resource "aws_apigatewayv2_vpc_link" "sportapp-vpc-link" {
  name               = "SportApp VPC Link"
  security_group_ids = [var.vpc_link_security_group]
  subnet_ids         = var.vpc_link_subnets
}
