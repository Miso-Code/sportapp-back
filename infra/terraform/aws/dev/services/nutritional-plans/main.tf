provider "aws" {
  region = "us-east-1"
}

data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "aws_secretsmanager_secret" "db_credentials" {
  name = "DB_CREDENTIALS_DEV"
}

data "aws_secretsmanager_secret" "services_urls" {
  name = "SERVICES_URLS_DEV"
}


data "terraform_remote_state" "resources" {
  backend = "remote"
  config = {
    organization = "MisoTeam"
    workspaces = {
      name = "aws-resources-dev"
    }
  }
}

// Register target group and listener rule
module "nutritional-plans-tg" {
  source                         = "../../../modules/elb/target_group"
  target_group_name              = "nutritional-plans-dev-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "nutritional-plans-listener-rule" {
  source                = "../../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/nutritional-plans/*"
  rule_priority         = 9
  rule_target_group_arn = module.nutritional-plans-tg.tg_arn
}

// Register task definition
module "nutritional-plans-task-def" {
  source                = "../../../modules/ecs/task_definition"
  service_name          = "nutritional-plans-dev"
  container_image       = "887664210442.dkr.ecr.us-east-1.amazonaws.com/nutritional-plans:develop"
  container_port        = 8000
  cpu                   = 256
  memory                = 512
  task_role_arn         = data.aws_iam_role.ecs_role.arn
  execution_role_arn    = data.aws_iam_role.ecs_role.arn
  environment_variables = [
    {
      "name" : "NUTRITIONAL_PLAN_ALERTS_QUEUE",
      "value" : data.terraform_remote_state.resources.outputs.nutritional_queue_name
    }
  ]
  secrets = [
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.db_credentials.arn}:NAME::"
      "name" : "DB_NAME"
    },
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.db_credentials.arn}:HOST::"
      "name" : "DB_HOST"
    },
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.db_credentials.arn}:PORT::"
      "name" : "DB_PORT"
    },
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.db_credentials.arn}:USERNAME::"
      "name" : "DB_USERNAME"
    },
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.db_credentials.arn}:PASSWORD::"
      "name" : "DB_PASSWORD"
    },
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.services_urls.arn}:SPORTAPP_SERVICES_BASE_URL::"
      "name" : "SPORTAPP_SERVICES_BASE_URL"
    }
  ]
}

// Register service
module "nutritional-plans-service" {
  source              = "../../../modules/ecs/service"
  service_name        = "nutritional-plans-dev-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.ecs_cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.nutritional-plans-tg.tg_arn
  task_definition_arn = module.nutritional-plans-task-def.task_arn
}


module "nutritional-plans-create-plan" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/nutritional-plans"
  special_path     = true
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "nutritional-plans-get-plan" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "GET"
  route_path       = "/nutritional-plans"
  special_path     = true
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "nutritional-plans-notify-caloric-intake" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/nutritional-plans/notify-caloric-intake"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}
