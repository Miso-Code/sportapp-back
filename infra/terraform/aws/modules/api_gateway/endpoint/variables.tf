variable "api_gateway_id" {
  description = "API Gateway ID"
  type        = string
}

variable "resource_id" {
  description = "API Gateway Resource ID"
  type        = string
}

variable "http_method" {
  description = "HTTP Method"
  type        = string
}

variable "authorization" {
  description = "Authorization"
  type        = string
  default     = "NONE"
}

variable "integration_type" {
  description = "Integration Type"
  type        = string
  default     = "HTTP"
}

variable "integration_uri" {
  description = "Integration URI"
  type        = string
}