variable "authorizer_name" {
  description = "The name of the authorizer"
  type        = string
}

variable "authorizer_scope" {
  description = "The scope of the authorizer"
  type        = string
}

variable "lambda_role_arn" {
  description = "The ARN of the Lambda role"
  type        = string
}

variable "authorizer_version" {
  description = "The version of the authorizer"
  type        = string
  default     = "latest"
}
