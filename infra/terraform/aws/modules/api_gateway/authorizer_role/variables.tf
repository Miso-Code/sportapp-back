variable "lambda_get_secrets_role_name" {
  description = "The name of the role that allows the Lambda function to get secrets from Secrets Manager"
  type        = string
  default     = "lambda-get-secrets-role"
}
