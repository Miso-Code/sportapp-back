output "cluster_id" {
  value = module.ecs_cluster.cluster_id
}

output "subnets" {
  value = [module.subnet_1.id, module.subnet_2.id, module.subnet_3.id]
}

output "security_groups" {
  value = [module.vpc.security_group_id]
}

output "vpc_id" {
  value = module.vpc.id
}