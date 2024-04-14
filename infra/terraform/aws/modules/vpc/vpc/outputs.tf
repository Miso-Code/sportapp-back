output "id" {
  value = aws_vpc.vpc.id
}

output "cidr_block" {
  value = aws_vpc.vpc.cidr_block
}

output "security_group_id" {
  value = aws_vpc.vpc.default_security_group_id
}

output "vpc_link_security_group_id" {
  value = aws_security_group.elb-api-gateway-sg.id
}
