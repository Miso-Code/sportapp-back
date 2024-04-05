resource "aws_apigatewayv2_api" "api" {
  name        = var.api_name
  description = var.api_description

  protocol_type = "HTTP"
}
