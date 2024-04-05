resource "aws_apigatewayv2_integration" "integration" {
  api_id           = var.api_id
  integration_type = "HTTP_PROXY"

  integration_method = var.route_integration_method
  integration_uri    = var.route_integration_uri

  request_parameters = {
    "append:header.user-id" = "$context.authorizer.user_id"
  }
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = var.api_id
  route_key = "${var.route_method} ${var.route_path}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}
