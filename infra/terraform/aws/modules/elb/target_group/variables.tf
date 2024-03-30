variable "target_group_name" {
  description = "The name of the target group"
  type        = string
}

variable "target_group_port" {
  description = "The port the target group listens on"
  type        = number
}

variable "target_group_protocol" {
  description = "The protocol the target group listens on"
  type        = string
}

variable "target_group_health_check_path" {
  description = "The path the target group uses for health checks"
  type        = string
}

variable "vpc_id" {
  description = "The VPC ID"
  type        = string
}