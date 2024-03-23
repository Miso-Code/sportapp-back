resource "aws_lb" "alb" {
  name                       = var.name
  internal                   = false
  load_balancer_type         = "application"
  subnets                    = var.subnets
  enable_deletion_protection = true
}