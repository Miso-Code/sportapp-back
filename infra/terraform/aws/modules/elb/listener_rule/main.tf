resource "aws_lb_listener_rule" "listener_rule" {
  listener_arn = var.listener_arn
  priority     = var.rule_priority

  action {
    type             = "forward"
    target_group_arn = var.rule_target_group_arn
  }

  condition {
    path_pattern {
      values = [var.rule_path_pattern]
    }
  }
}
