data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "terraform_remote_state" "resources" {
  backend = "local"
  config  = {
    path = "../resources/terraform.tfstate"
  }
}

module "users-tg" {
  source                         = "../modules/aws_elb/target_group"
  target_group_name              = "users-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id = data.terraform_remote_state.resources.outputs.vpc_id
}

module "users-task-def" {
  source                    = "../modules/aws_ecs/task_definition"
  name                      = "users-task-def"
  container_definition_file = "../../../../projects/users/ecs-container-definition.json"
  cpu                       = 256
  memory                    = 512
  execution_role_arn        = data.aws_iam_role.ecs_role.arn
  task_role_arn             = data.aws_iam_role.ecs_role.arn
}

module "users-service" {
  source              = "../modules/aws_ecs/service"
  service_name        = "users-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.users-tg.tg_arn
  task_definition_arn = module.users-task-def.task_arn
}
