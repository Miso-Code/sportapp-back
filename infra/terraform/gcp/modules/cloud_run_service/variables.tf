variable "name" {
  description = "The name of the Cloud Run service"
  type        = string
}

variable "location" {
  description = "The location where the Cloud Run service will be deployed"
  type        = string
}

variable "image" {
  description = "The container image to deploy"
  type        = string
}

variable "port" {
  description = "The port on which the container listens"
  type        = number
}

variable "service_account" {
  description = "The service account to use for the container"
  type        = string
}

variable "memory_limit" {
  description = "The amount of memory to allocate to the container"
  type        = string
  default     = "512Mi"
}

variable "cpu_limit" {
  description = "The amount of CPU cores to allocate to the container"
  type        = string
  default     = "1"
}

variable "max_instance_count" {
  description = "The maximum number of container instances to run"
  type        = number
  default     = 1
}

variable "env" {
  description = "A map of environment variables to be made available to the container"
  type        = map(string)
}

variable "jwt_secret_id" {
  description = "The ID of the secret containing the JWT secret"
  type        = string
}
