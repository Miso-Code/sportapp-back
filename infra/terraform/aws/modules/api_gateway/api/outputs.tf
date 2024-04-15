output "gateway_id" {
  value = aws_apigatewayv2_api.api.id
}

output "execution_arn" {
  value = aws_apigatewayv2_api.api.execution_arn
}

output "vpc_link_id" {
  value = aws_apigatewayv2_vpc_link.sportapp-vpc-link.id
}
