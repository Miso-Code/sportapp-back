resource "aws_api_gateway_method" "endpoint_method" {
  rest_api_id   = var.api_gateway_id
  resource_id   = var.resource_id
  http_method   = var.http_method
  authorization = var.authorization
}

resource "aws_api_gateway_integration" "endpoint_integration" {
  rest_api_id             = var.api_gateway_id
  resource_id             = var.resource_id
  http_method             = var.http_method
  integration_http_method = var.http_method
  type                    = var.integration_type
  uri                     = var.integration_uri
}

