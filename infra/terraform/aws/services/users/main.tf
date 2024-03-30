data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "terraform_remote_state" "resources" {
  backend = "local"
  config  = {
    path = "../../resources/terraform.tfstate"
  }
}

// Register target group and listener rule
module "users-tg" {
  source                         = "../../modules/elb/target_group"
  target_group_name              = "users-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "users-listener-rule" {
  source                = "../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/users/*"
  rule_priority         = 1
  rule_target_group_arn = module.users-tg.tg_arn
}

// Register task definition
module "users-task-def" {
  source                    = "../../modules/ecs/task_definition"
  name                      = "users-task-def"
  container_definition_file = "../../../../../projects/users/ecs-container-definition.json"
  cpu                       = 256
  memory                    = 512
  execution_role_arn        = data.aws_iam_role.ecs_role.arn
  task_role_arn             = data.aws_iam_role.ecs_role.arn
}

// Register service
module "users-service" {
  source              = "../../modules/ecs/service"
  service_name        = "users-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.ecs_cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.users-tg.tg_arn
  task_definition_arn = module.users-task-def.task_arn
}

// Login and Register Service API Gateway endpoints
module "users-login-resource" {
  source        = "../../modules/api_gateway/resource"
  api_id        = data.terraform_remote_state.resources.outputs.api_gateway_id
  api_parent_id = data.terraform_remote_state.resources.outputs.api_gateway_root_resource_id
  api_path      = "login"
}

module "users-login-endpoint" {
  source          = "../../modules/api_gateway/endpoint"
  api_gateway_id  = data.terraform_remote_state.resources.outputs.api_gateway_id
  http_method     = "POST"
  integration_uri = "http://${data.terraform_remote_state.resources.outputs.elb_dns_name}/users/login"
  resource_id     = module.users-login-resource.resource_id
}

module "users-register-resource" {
  source        = "../../modules/api_gateway/resource"
  api_id        = data.terraform_remote_state.resources.outputs.api_gateway_id
  api_parent_id = data.terraform_remote_state.resources.outputs.api_gateway_root_resource_id
  api_path      = "register"
}

module "users-register-endpoint" {
  source          = "../../modules/api_gateway/endpoint"
  api_gateway_id  = data.terraform_remote_state.resources.outputs.api_gateway_id
  http_method     = "POST"
  integration_uri = "http://${data.terraform_remote_state.resources.outputs.elb_dns_name}/users/register"
  resource_id     = module.users-register-resource.resource_id
}

// User Service API Gateway endpoints

module "users-base-path-resource" {
  source        = "../../modules/api_gateway/resource"
  api_id        = data.terraform_remote_state.resources.outputs.api_gateway_id
  api_parent_id = data.terraform_remote_state.resources.outputs.api_gateway_root_resource_id
  api_path      = "users"
}

// API Gateway deployment

module "users-deployment" {
  source               = "../../modules/api_gateway/deployment"
  api_gateway_id       = data.terraform_remote_state.resources.outputs.api_gateway_id

  depends_on = [
    module.users-login-endpoint,
    module.users-register-endpoint
  ]
}
