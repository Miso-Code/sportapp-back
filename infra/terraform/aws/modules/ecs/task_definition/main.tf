resource "aws_ecs_task_definition" "task" {
  family                   = var.name
  container_definitions    = file(var.container_definition_file)
  requires_compatibilities = ["FARGATE"]
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
  network_mode       = "awsvpc"
  task_role_arn      = var.task_role_arn
  execution_role_arn = var.execution_role_arn
  cpu                = var.cpu
  memory             = var.memory
}