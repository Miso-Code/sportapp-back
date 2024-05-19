provider "aws" {
  region = "us-east-1"
}

data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "aws_secretsmanager_secret" "db_credentials" {
  name = "DB_CREDENTIALS_DEV"
}

data "aws_secretsmanager_secret" "firebase_credentials" {
  name = "GCLOUD_CREDENTIALS"
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
module "alerts-tg" {
  source                         = "../../../modules/elb/target_group"
  target_group_name              = "alerts-dev-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "alerts-listener-rule" {
  source                = "../../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/alerts/*"
  rule_priority         = 8
  rule_target_group_arn = module.alerts-tg.tg_arn
}

// Register task definition
module "alerts-task-def" {
  source                = "../../../modules/ecs/task_definition"
  service_name          = "alerts-dev"
  container_image       = "887664210442.dkr.ecr.us-east-1.amazonaws.com/alerts:develop"
  container_port        = 8000
  cpu                   = 256
  memory                = 512
  task_role_arn         = data.aws_iam_role.ecs_role.arn
  execution_role_arn    = data.aws_iam_role.ecs_role.arn
  environment_variables = [
    {
      "name" : "ADVERSE_INCIDENTS_ALERTS_QUEUE",
      "value" : data.terraform_remote_state.resources.outputs.adverse_incidents_queue_name
    },
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
      "valueFrom" : "${data.aws_secretsmanager_secret.firebase_credentials.arn}:GCLOUD_CREDENTIALS::"
      "name" : "FIREBASE_CERT"
    }
  ]
}

// Register service
module "alerts-service" {
  source              = "../../../modules/ecs/service"
  service_name        = "alerts-dev-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.ecs_cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.alerts-tg.tg_arn
  task_definition_arn = module.alerts-task-def.task_arn
}


module "alerts-register-device-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/alerts/register-device"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "alerts-disable-device-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "PUT"
  route_path       = "/alerts/disable-device"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "alerts-get-device-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "GET"
  route_path       = "/alerts/device"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "alerts-send-test-alert-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/alerts/send-test-alert"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}
