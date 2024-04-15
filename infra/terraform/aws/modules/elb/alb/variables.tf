variable "name" {
  description = "The name of the Load Balancer"
  type        = string
}

variable "subnets" {
  description = "The subnets to attach the Load Balancer to"
  type        = list(string)
}
