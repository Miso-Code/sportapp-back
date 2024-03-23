variable "database_name" {
  description = "The name of the database"
  type        = string
}

variable "instance_name" {
  description = "The name of the instance"
  type        = string
}

variable "region" {
  description = "The region in which the resources will be created"
  type        = string
}

variable "database_version" {
  description = "The version of the database"
  type        = string
  default     = "POSTGRES_15"
}

variable "tier" {
  description = "The tier of the database"
  type        = string
  default     = "db-f1-micro"
}

variable "deletion_protection" {
  description = "The deletion protection of the database"
  type        = bool
  default     = false
}

variable "username" {
  description = "The username of the database"
  type        = string
}

variable "password" {
  description = "The password of the database"
  type        = string
}