variable "listener_arn" {
  description = "The ARN of the listener"
  type        = string
}

variable "rule_priority" {
  description = "The priority of the rule"
  type        = number

}
variable "rule_target_group_arn" {
  description = "The ARN of the target group"
  type        = string
}

variable "rule_path_pattern" {
  description = "The path pattern to match"
  type        = string
}
