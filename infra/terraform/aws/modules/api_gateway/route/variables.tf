variable "api_id" {
  description = "API Gateway ID"
  type        = string
}

variable "route_path" {
  description = "Route path"
  type        = string
}

variable "route_method" {
  description = "Route method"
  type        = string
}

variable "route_integration_method" {
  description = "Route integration method"
  type        = string
}

variable "route_integration_uri" {
  description = "Route integration URI"
  type        = string
}
