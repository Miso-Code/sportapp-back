provider "aws" {
  region = "us-east-1"
}

data "aws_iam_role" "ecs_role" {
  name = "ecsTaskExecutionRole"
}

data "aws_secretsmanager_secret" "db_credentials" {
  name = "DB_CREDENTIALS_PROD"
}

data "aws_secretsmanager_secret" "jwt_secret" {
  name = "JWT_SECRET"
}

data "aws_secretsmanager_secret" "services_urls" {
  name = "SERVICES_URLS_PROD"
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
module "users-tg" {
  source                         = "../../../modules/elb/target_group"
  target_group_name              = "users-tg"
  target_group_port              = 8000
  target_group_protocol          = "HTTP"
  target_group_health_check_path = "/ping"
  vpc_id                         = data.terraform_remote_state.resources.outputs.vpc_id
}

module "users-listener-rule" {
  source                = "../../../modules/elb/listener_rule"
  listener_arn          = data.terraform_remote_state.resources.outputs.elb_listener_arn
  rule_path_pattern     = "/users/*"
  rule_priority         = 1
  rule_target_group_arn = module.users-tg.tg_arn
}

// Register task definition
module "users-task-def" {
  source                = "../../../modules/ecs/task_definition"
  service_name          = "users"
  container_image       = "887664210442.dkr.ecr.us-east-1.amazonaws.com/users:latest"
  container_port        = 8000
  cpu                   = 256
  memory                = 512
  task_role_arn         = data.aws_iam_role.ecs_role.arn
  execution_role_arn    = data.aws_iam_role.ecs_role.arn
  environment_variables = [
    {
      "name" : "ACCESS_TOKEN_EXPIRE_MINUTES",
      "value" : "30"
    },
    {
      "name" : "TOTAL_USERS_BY_RUN",
      "value" : "200"
    },
    {
      "name" : "SYNC_EVERY_MINUTES",
      "value" : "5"
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
      "valueFrom" : "${data.aws_secretsmanager_secret.jwt_secret.arn}:JWT_SECRET::"
      "name" : "JWT_SECRET_KEY"
    },
    {
      "valueFrom" : "${data.aws_secretsmanager_secret.services_urls.arn}:SPORTAPP_SERVICES_BASE_URL::"
      "name" : "SPORTAPP_SERVICES_BASE_URL"
    }
  ]
}

// Register service
module "users-service" {
  source              = "../../../modules/ecs/service"
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
module "users-registration-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/users/registration"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-login-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "POST"
  route_path       = "/users/login"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-complete-registration-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "PATCH"
  route_path       = "/users/complete-registration"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

// Profile APIs

module "users-get-personal-profile-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "GET"
  route_path       = "/users/profiles/personal"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-update-personal-profile-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "PATCH"
  route_path       = "/users/profiles/personal"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-get-sports-profile-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "GET"
  route_path       = "/users/profiles/sports"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-update-sports-profile-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "PATCH"
  route_path       = "/users/profiles/sports"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-get-nutritional-profile-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "GET"
  route_path       = "/users/profiles/nutritional"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-update-nutritional-profile-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "PATCH"
  route_path       = "/users/profiles/nutritional"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-get-all-nutritional-limitations-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "GET"
  route_path       = "/users/nutritional-limitations"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}

module "users-update-user-plan-route" {
  source           = "../../../modules/api_gateway/route"
  api_id           = data.terraform_remote_state.resources.outputs.api_gateway_id
  route_method     = "PATCH"
  route_path       = "/update-plan"
  elb_listener_arn = data.terraform_remote_state.resources.outputs.elb_listener_arn
  vpc_link_id      = data.terraform_remote_state.resources.outputs.vpc_link_id
}
