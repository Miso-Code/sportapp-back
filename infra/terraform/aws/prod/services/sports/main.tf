provider "aws" {
  region = "us-east-1"
}

data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "aws_secretsmanager_secret" "db_credentials" {
  name = "DB_CREDENTIALS_PROD"
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
module "sports-tg" {
  source                         = "../../../modules/elb/target_group"
  target_group_name              = "sports-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "sports-listener-rule" {
  source                = "../../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/sports/*"
  rule_priority         = 2
  rule_target_group_arn = module.sports-tg.tg_arn
}

// Register task definition
module "sports-task-def" {
  source                = "../../../modules/ecs/task_definition"
  service_name          = "sports"
  container_image       = "887664210442.dkr.ecr.us-east-1.amazonaws.com/sports:latest"
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
    }
  ]
}

// Register service
module "sports-service" {
  source              = "../../../modules/ecs/service"
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
  source                   = "../../../modules/api_gateway/route"
  api_id                   = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method             = "GET"
  route_path               = "/sports"
  elb_listener_arn         = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id              = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "sports-get-by-id-route" {
  source                   = "../../../modules/api_gateway/route"
  api_id                   = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method             = "GET"
  route_path               = "/sports/{id}"
  elb_listener_arn         = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id              = data.terraform_remote_state.resources.outputs.vpc_link_id
}
