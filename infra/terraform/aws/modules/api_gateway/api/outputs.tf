output "gateway_id" {
  value = aws_api_gateway_rest_api.api.id
}

output "gateway_root_resource_id" {
  value = aws_api_gateway_rest_api.api.root_resource_id
}
