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
module "sports-tg" {
  source                         = "../../modules/elb/target_group"
  target_group_name              = "sports-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "sports-listener-rule" {
  source                = "../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/sports/*"
  rule_priority         = 2
  rule_target_group_arn = module.sports-tg.tg_arn
}

// Register task definition
module "sports-task-def" {
  source                    = "../../modules/ecs/task_definition"
  name                      = "sports-task-def"
  container_definition_file = "../../../../../projects/sports/ecs-container-definition.json"
  cpu                       = 256
  memory                    = 512
  execution_role_arn        = data.aws_iam_role.ecs_role.arn
  task_role_arn             = data.aws_iam_role.ecs_role.arn
}

// Register service
module "sports-service" {
  source              = "../../modules/ecs/service"
  service_name        = "sports-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.ecs_cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.sports-tg.tg_arn
  task_definition_arn = module.sports-task-def.task_arn
}

// User Service API Gateway endpoints

module "sports-get-all-route" {
  source                   = "../../modules/api_gateway/route"
  api_id                   = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_integration_method = "GET"
  route_integration_uri    = "http://${data.terraform_remote_state.resources.outputs.elb_dns_name}/sports/"
  route_method             = "GET"
  route_path               = "/sports/"
}

module "sports-get-by-id-route" {
  source                   = "../../modules/api_gateway/route"
  api_id                   = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_integration_method = "GET"
  route_integration_uri    = "http://${data.terraform_remote_state.resources.outputs.elb_dns_name}/sports/{id}"
  route_method             = "GET"
  route_path               = "/sports/{id}"
}
