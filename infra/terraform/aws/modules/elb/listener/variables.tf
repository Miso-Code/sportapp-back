variable "load_balancer_arn" {
  description = "The ARN of the load balancer"
  type        = string
}

variable "listener_port" {
  description = "The port on which the load balancer is listening"
  type        = number
}

variable "listener_protocol" {
  description = "The protocol on which the load balancer is listening"
  type        = string
}
