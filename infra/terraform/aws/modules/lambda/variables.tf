variable "function_name" {
  description = "The name of the function"
  type        = string
}

variable "image_uri" {
  description = "The URI of the image"
  type        = string
}

variable "environment_variables" {
  description = "The environment variables"
  type        = map(string)
}
