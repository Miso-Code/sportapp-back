resource "aws_vpc" "vpc" {
  cidr_block       = var.vpc_cidr
  instance_tenancy = "default"
  tags = {
    Name = var.vpc_name
  }
}

resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.vpc_name}-gateway"
  }
}

resource "aws_route_table" "route_table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gateway.id
  }
}

resource "aws_main_route_table_association" "association" {
  vpc_id         = aws_vpc.vpc.id
  route_table_id = aws_route_table.route_table.id
}

resource "aws_security_group" "elb-api-gateway-sg" {
  name        = "elb-api-gateway-sg"
  vpc_id      = aws_vpc.vpc.id
  description = "Used with VPC Link for API Gateway"

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

}

resource "aws_vpc_security_group_ingress_rule" "elb-api-gateway-sg-ingress" {
  security_group_id = aws_security_group.elb-api-gateway-sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 8000
  ip_protocol       = "tcp"
  to_port           = 8000
}


data "aws_security_group" "default" {
  id = aws_vpc.vpc.default_security_group_id
}
#
resource "aws_vpc_security_group_ingress_rule" "default-sg-allow-elb-api-gateway-sg-ingress" {
  security_group_id = data.aws_security_group.default.id
  from_port         = 8000
  ip_protocol       = "tcp"
  to_port           = 8000
  referenced_security_group_id = aws_security_group.elb-api-gateway-sg.id
}
