provider "aws" {
  region = "us-east-1"
}

data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "aws_secretsmanager_secret" "db_credentials" {
  name = "DB_CREDENTIALS_PROD"
}

data "aws_secretsmanager_secret" "api_key" {
  name = "API_KEY"
}

data "terraform_remote_state" "resources" {
  backend = "remote"
  config = {
    organization = "MisoTeam"
    workspaces = {
      name = "aws-resources-prod"
    }
  }
}

// Register target group and listener rule
module "miso-stripe-tg" {
  source                         = "../../../modules/elb/target_group"
  target_group_name              = "miso-stripe-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "miso-stripe-listener-rule" {
  source                = "../../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/miso-stripe/*"
  rule_priority         = 5
  rule_target_group_arn = module.miso-stripe-tg.tg_arn
}

// Register task definition
module "miso-stripe-task-def" {
  source                = "../../../modules/ecs/task_definition"
  service_name          = "miso-stripe"
  container_image       = "887664210442.dkr.ecr.us-east-1.amazonaws.com/miso-stripe:develop"
  container_port        = 8000
  cpu                   = 256
  memory                = 512
  task_role_arn         = data.aws_iam_role.ecs_role.arn
  execution_role_arn    = data.aws_iam_role.ecs_role.arn
  environment_variables = []
  secrets               = [
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
      "valueFrom" : "${data.aws_secretsmanager_secret.api_key.arn}:MISO_STRIPE::"
      "name" : "API_KEY"
    }
  ]
}

// Register service
module "miso-stripe-service" {
  source              = "../../../modules/ecs/service"
  service_name        = "miso-stripe-service"
  desired_count       = 1
  container_port      = 8000
  cluster_id          = data.terraform_remote_state.resources.outputs.ecs_cluster_id
  security_groups     = data.terraform_remote_state.resources.outputs.security_groups
  subnets             = data.terraform_remote_state.resources.outputs.subnets
  target_group_arn    = module.miso-stripe-tg.tg_arn
  task_definition_arn = module.miso-stripe-task-def.task_arn
}


module "miso-stripe-create-card-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/miso-stripe/cards"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "miso-stripe-get-cards-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "GET"
  route_path       = "/miso-stripe/cards"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "miso-stripe-add-balance-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/miso-stripe/balances/add"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "miso-stripe-remove-balance-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/miso-stripe/balances/remove"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "miso-stripe-payment-route-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/miso-stripe/payments"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}
