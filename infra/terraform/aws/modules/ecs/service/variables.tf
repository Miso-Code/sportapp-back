variable "service_name" {
  description = "The name of the service"
  type        = string
}

variable "cluster_id" {
  description = "The ID of the cluster"
  type        = string
}

variable "task_definition_arn" {
  description = "The task definition to use"
  type        = string
}

variable "desired_count" {
  description = "The number of tasks to run"
  type        = number
}

variable "container_port" {
  description = "The port to use"
  type        = number
}

variable "subnets" {
  description = "The subnets to use"
  type        = list(string)
}

variable "security_groups" {
  description = "The security groups to use"
  type        = list(string)
}

variable "target_group_arn" {
  description = "The target group to use"
  type        = string
}