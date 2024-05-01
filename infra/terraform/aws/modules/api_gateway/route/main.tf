resource "aws_apigatewayv2_integration" "integration" {
  api_id           = var.api_id
  integration_type = "HTTP_PROXY"
  connection_type  = "VPC_LINK"
  connection_id    = var.vpc_link_id

  integration_method = var.route_method
  integration_uri    = var.elb_listener_arn

  request_parameters = {
    "append:header.user-id" = "$context.authorizer.user_id"
    "overwrite:path"        = var.special_path ? "${var.route_path}/" : "$request.path"
  }
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = var.api_id
  route_key = "${var.route_method} ${var.route_path}"
  target    = "integrations/${aws_apigatewayv2_integration.integration.id}"
}
