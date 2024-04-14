variable "api_id" {
  description = "API Gateway ID"
  type        = string
}

variable "route_path" {
  description = "Route path"
  type        = string
}

variable "route_method" {
  description = "Route method"
  type        = string
}

variable "vpc_link_id" {
  description = "VPC Link ID"
  type        = string
}

variable "elb_listener_arn" {
  description = "ELB Listener ARN"
  type        = string
}
