data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "terraform_remote_state" "resources" {
  backend = "local"
  config = {
    path = "../../resources/terraform.tfstate"
  }
}

// Register target group and listener rule
module "sport-sessions-tg" {
  source                         = "../../modules/elb/target_group"
  target_group_name              = "sport-sessions-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "sport-sessions-listener-rule" {
  source                = "../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/sport-sessions/*"
  rule_priority         = 1
  rule_target_group_arn = module.sport-sessions-tg.tg_arn
}

// Register task definition
module "sport-sessions-task-def" {
  source                    = "../../modules/ecs/task_definition"
  name                      = "sport-sessions-task-def"
  container_definition_file = "../../../../../projects/sport-sessions/ecs-container-definition.json"
  cpu                       = 256
  memory                    = 512
  execution_role_arn        = data.aws_iam_role.ecs_role.arn
  task_role_arn             = data.aws_iam_role.ecs_role.arn
}

// Register service
module "sport-sessions-service" {
  source              = "../../modules/ecs/service"
  service_name        = "sport-sessions-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.ecs_cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.sport-sessions-tg.tg_arn
  task_definition_arn = module.sport-sessions-task-def.task_arn
}

// Login and Register Service API Gateway endpoints
module "sport-sessions-register-route" {
  source                   = "../../modules/api_gateway/route"
  api_id                   = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_integration_method = "POST"
  route_integration_uri    = "http://${data.terraform_remote_state.resources.outputs.elb_dns_name}/sport-sessions"
  route_method             = "POST"
  route_path               = "/sport-sessions/"
}
