provider "aws" {
  region = "us-east-1"
}

data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "aws_secretsmanager_secret" "api_key" {
  name = "API_KEY"
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
module "adverse-incidents-provider-tg" {
  source                         = "../../../modules/elb/target_group"
  target_group_name              = "incidents-provider-dev-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "adverse-incidents-provider-listener-rule" {
  source                = "../../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/incidents/*"
  rule_priority         = 11
  rule_target_group_arn = module.adverse-incidents-provider-tg.tg_arn
}

// Register task definition
module "adverse-incidents-provider-task-def" {
  source                = "../../../modules/ecs/task_definition"
  service_name          = "adverse-incidents-provider-dev"
  container_image       = "887664210442.dkr.ecr.us-east-1.amazonaws.com/adverse-incidents-provider:develop"
  container_port        = 8000
  cpu                   = 256
  memory                = 512
  task_role_arn         = data.aws_iam_role.ecs_role.arn
  execution_role_arn    = data.aws_iam_role.ecs_role.arn
  environment_variables = [
    {
      "name" : "MAX_ADVERSE_INCIDENTS",
      "value" : 5
    },
    {
      "name" : "ADVERSE_INCIDENTS_AFFECTED_RANGE",
      "value" : 0.5
    }
  ]
  secrets = [
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.api_key.arn}:INCIDENTS::"
      "name" : "INCIDENTS_API_KEY"
    }
  ]
}

// Register service
module "adverse-incidents-provider-service" {
  source              = "../../../modules/ecs/service"
  service_name        = "adverse-incidents-provider-dev-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.ecs_cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.adverse-incidents-provider-tg.tg_arn
  task_definition_arn = module.adverse-incidents-provider-task-def.task_arn
}

module "alerts-send-test-alert-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/incidents"
  special_path     = true
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}
