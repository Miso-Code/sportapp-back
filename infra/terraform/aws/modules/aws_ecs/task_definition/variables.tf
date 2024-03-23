variable "name" {
  description = "The name of the task definition"
  type        = string
}

variable "container_definition_file" {
  description = "Path to the container definitions file"
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