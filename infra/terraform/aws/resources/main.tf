provider "aws" {
  region = "us-east-1"
}

data "aws_secretsmanager_secret" "db_credentials" {
  name = "DB_CREDENTIALS"
}

data "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = data.aws_secretsmanager_secret.db_credentials.id
}

module "vpc" {
  source   = "../modules/aws_vpc/vpc"
  vpc_name = "sportapp-vpc"
  vpc_cidr = "10.0.0.0/16"
}

module "subnet_1" {
  source            = "../modules/aws_vpc/subnet"
  vpc_id            = module.vpc.id
  subnet_name       = "sportapp-subnet"
  subnet_cidr_block = cidrsubnet(module.vpc.cidr_block, 8, 1)
  availability_zone = "us-east-1a"
  depends_on        = [module.vpc]
}

module "subnet_2" {
  source            = "../modules/aws_vpc/subnet"
  vpc_id            = module.vpc.id
  subnet_name       = "sportapp-subnet"
  subnet_cidr_block = cidrsubnet(module.vpc.cidr_block, 8, 2)
  availability_zone = "us-east-1b"
  depends_on        = [module.vpc]
}

module "subnet_3" {
  source            = "../modules/aws_vpc/subnet"
  vpc_id            = module.vpc.id
  subnet_name       = "sportapp-subnet"
  subnet_cidr_block = cidrsubnet(module.vpc.cidr_block, 8, 3)
  availability_zone = "us-east-1c"
  depends_on        = [module.vpc]
}

module "db" {
  source        = "../modules/aws_rds_instance"
  database_name = "sportapp"
  username      = jsondecode(nonsensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).username
  password      = jsondecode(nonsensitive(data.aws_secretsmanager_secret_version.db_credentials.secret_string)).password
  depends_on    = [module.vpc]
}

module "nutritional_queue" {
  source     = "../modules/aws_sqs_queue"
  queue_name = "nutritional_plan_queue.fifo"
}

module "adverse_incidents_queue" {
  source     = "../modules/aws_sqs_queue"
  queue_name = "adverse_incidents_queue.fifo"
}

module "application_load_balancer" {
  source     = "../modules/aws_elb/alb"
  name       = "sportapp-alb"
  subnets    = [module.subnet_1.id, module.subnet_2.id, module.subnet_3.id]
  depends_on = [module.vpc, module.subnet_1, module.subnet_2, module.subnet_3]
}

module "application_load_balancer_listener" {
  source     = "../modules/aws_elb/alb_listener"
  alb_arn    = module.application_load_balancer.arn
  depends_on = [module.application_load_balancer]
}

module "ecs_cluster" {
  source       = "../modules/aws_ecs/cluster"
  cluster_name = "sportapp-cluster"
}
