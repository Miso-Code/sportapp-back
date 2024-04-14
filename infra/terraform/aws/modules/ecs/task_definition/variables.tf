variable "service_name" {
  description = "The name of the service"
  type        = string
}

variable "execution_role_arn" {
  description = "The ARN of the task execution role that grants the ECS agent permission to make AWS API calls on your behalf"
  type        = string
}

variable "task_role_arn" {
  description = "The ARN of the IAM role that containers in this task can assume"
  type        = string
}

variable "cpu" {
  description = "The number of CPU units used by the task"
  type        = number
}

variable "memory" {
  description = "The amount (in MiB) of memory used by the task"
  type        = number
}

variable "container_port" {
  description = "The port number on the container that is bound to the user-specified or automatically assigned host port"
  type        = number
}

variable "container_image" {
  description = "Container image"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for the container"
  type        = list(object({
    name  = string
    value = string
  }))
}

variable "secrets" {
  description = "Secrets for the container"
  type        = list(object({
    valueFrom = string
    name      = string
  }))
}
