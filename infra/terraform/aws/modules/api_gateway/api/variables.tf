variable "api_name" {
  description = "The name of the API Gateway REST API"
  type        = string
}

variable "api_description" {
  description = "The description of the API Gateway REST API"
  type        = string
}

variable "vpc_link_subnets" {
  description = "The subnets to attach to the VPC link"
  type        = list(string)
}

variable "vpc_link_security_group" {
  description = "The security group to attach to the VPC link"
  type        = string
}
