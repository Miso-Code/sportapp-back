resource "aws_ecs_task_definition" "task" {
  family                   = "${var.service_name}-task-def"
  requires_compatibilities = ["FARGATE"]
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
  network_mode          = "awsvpc"
  task_role_arn         = var.task_role_arn
  execution_role_arn    = var.execution_role_arn
  cpu                   = var.cpu
  memory                = var.memory
  container_definitions = jsonencode([
    {
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
          appProtocol   = "http"
        }
      ]
      image       = var.container_image
      essential   = true
      name        = "${var.service_name}-service"
      environment = var.environment_variables
      secrets     = var.secrets
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.service_name}-service"
          awslogs-region        = "us-east-1"
          awslogs-create-group  = "true"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
