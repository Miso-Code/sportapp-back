variable "database_name" {
  description = "The name of the database"
  type        = string
}

variable "instance_class" {
  description = "The instance class of the database"
  type        = string
  default     = "db.t4g.micro"
}

variable "username" {
  description = "The username of the database"
  type        = string
}

variable "password" {
  description = "The password of the database"
  type        = string
}

variable "subnet_ids" {
  description = "The subnet IDs of the database"
  type        = list(string)
}

variable "environment" {
  description = "The environment of the database"
  type        = string
  default     = ""
}
