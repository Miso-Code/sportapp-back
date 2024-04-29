provider "aws" {
  region = "us-east-1"
}

data "aws_secretsmanager_secret" "db_credentials" {
  name = "DB_CREDENTIALS_QA"
}

data "aws_secretsmanager_secret" "services-urls" {
  name = "SERVICES_URLS_QA"
}

data "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = data.aws_secretsmanager_secret.db_credentials.id
}

# Network configuration

module "vpc" {
  source   = "../../modules/vpc/vpc"
  vpc_name = "sportapp-qa-vpc"
  vpc_cidr = "10.0.0.0/16"
}

module "subnet_1" {
  source            = "../../modules/vpc/subnet"
  vpc_id            = module.vpc.id
  subnet_name       = "sportapp-qa-subnet-1"
  subnet_cidr_block = cidrsubnet(module.vpc.cidr_block, 8, 1)
  availability_zone = "us-east-1a"
  depends_on        = [module.vpc]
}

module "subnet_2" {
  source            = "../../modules/vpc/subnet"
  vpc_id            = module.vpc.id
  subnet_name       = "sportapp-qa-subnet-2"
  subnet_cidr_block = cidrsubnet(module.vpc.cidr_block, 8, 2)
  availability_zone = "us-east-1b"
  depends_on        = [module.vpc]
}

module "subnet_3" {
  source            = "../../modules/vpc/subnet"
  vpc_id            = module.vpc.id
  subnet_name       = "sportapp-qa-subnet-3"
  subnet_cidr_block = cidrsubnet(module.vpc.cidr_block, 8, 3)
  availability_zone = "us-east-1c"
  depends_on        = [module.vpc]
}

# Database configuration

module "db" {
  source        = "../../modules/rds"
  database_name = "sportapp"
  environment   = "qa"
  username      = jsondecode(sensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).USERNAME
  password      = jsondecode(sensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).PASSWORD
  subnet_ids    = [module.subnet_1.id, module.subnet_2.id, module.subnet_3.id]
  depends_on    = [module.subnet_1, module.subnet_2, module.subnet_3]
}

resource "aws_secretsmanager_secret_version" "db_credentials_version" {
  secret_id     = data.aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    USERNAME = jsondecode(sensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).USERNAME
    PASSWORD = jsondecode(sensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).PASSWORD
    PORT     = jsondecode(sensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).PORT
    HOST     = module.db.host
    NAME     = jsondecode(sensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).NAME
  })
  depends_on = [module.db]
}

# Load balancer configuration

module "application_load_balancer" {
  source     = "../../modules/elb/alb"
  name       = "sportapp-qa-alb"
  subnets    = [module.subnet_1.id, module.subnet_2.id, module.subnet_3.id]
  depends_on = [module.vpc, module.subnet_1, module.subnet_2, module.subnet_3]
}

module "application_load_balancer_listener" {
  source            = "../../modules/elb/listener"
  listener_port     = 8000
  listener_protocol = "HTTP"
  load_balancer_arn = module.application_load_balancer.arn
  depends_on        = [module.application_load_balancer]
}

# API Gateway configuration

module "api_gateway" {
  source                  = "../../modules/api_gateway/api"
  api_description         = "Sportapp API Gateway"
  api_name                = "sportapp-qa-gateway"
  vpc_link_security_group = module.vpc.vpc_link_security_group_id
  vpc_link_subnets        = [module.subnet_1.id, module.subnet_2.id, module.subnet_3.id]
}

resource "aws_apigatewayv2_stage" "qa" {
  api_id      = module.api_gateway.gateway_id
  name        = "qa"
  auto_deploy = true
}

// Update services URLS
resource "aws_secretsmanager_secret_version" "services-urls-secret" {
  secret_id     = data.aws_secretsmanager_secret.services-urls.id
  secret_string = jsonencode({
    SPORTAPP_SERVICES_BASE_URL = aws_apigatewayv2_stage.qa.invoke_url
  })
}


# API Gateway authorizer configuration

module "authorizer_role" {
  source = "../../modules/api_gateway/authorizer_role"
  environment = "qa"
}

module "api_gateway_free_plan_authorizer" {
  source             = "../../modules/api_gateway/authorizer"
  authorizer_name    = "FreePlanAuthorizer-Dev"
  authorizer_scope   = "free"
  lambda_role_arn    = module.authorizer_role.role_arn
  authorizer_version = "develop"
}

module "api_gateway_intermediate_plan_authorizer" {
  source             = "../../modules/api_gateway/authorizer"
  authorizer_name    = "IntermediatePlanAuthorizer-Dev"
  authorizer_scope   = "intermediate"
  lambda_role_arn    = module.authorizer_role.role_arn
  authorizer_version = "develop"
}

module "api_gateway_premium_plan_authorizer" {
  source             = "../../modules/api_gateway/authorizer"
  authorizer_name    = "PremiumPlanAuthorizer-Dev"
  authorizer_scope   = "premium"
  lambda_role_arn    = module.authorizer_role.role_arn
  authorizer_version = "develop"
}

module "api_gateway_business_partner_authorizer" {
  source             = "../../modules/api_gateway/authorizer"
  authorizer_name    = "BusinessPartnerAuthorizer-Dev"
  authorizer_scope   = "business_partner"
  lambda_role_arn    = module.authorizer_role.role_arn
  authorizer_version = "develop"
}

# ECS configuration

module "ecs_cluster" {
  source       = "../../modules/ecs/cluster"
  cluster_name = "sportapp-qa-cluster"
  depends_on   = [module.vpc]
}

# SQS configuration

module "nutritional_queue" {
  source     = "../../modules/sqs"
  queue_name = "nutritional_plan_queue_dev.fifo"
}

module "adverse_incidents_queue" {
  source     = "../../modules/sqs"
  queue_name = "adverse_incidents_queue_dev.fifo"
}
