# output "subnets" {
#   value = [module.subnet_1.id, module.subnet_2.id, module.subnet_3.id]
# }
#
# output "security_groups" {
#   value = [module.vpc.security_group_id]
# }
#
# output "vpc_id" {
#   value = module.vpc.id
# }
#
# output "elb_listener_arn" {
#   value = module.application_load_balancer_listener.listener_arn
# }
#
# output "elb_dns_name" {
#   value = module.application_load_balancer.elb_dns
# }
#
# output "ecs_cluster_id" {
#   value = module.ecs_cluster.cluster_id
# }

output "api_gateway_id" {
  value = module.api_gateway.gateway_id
}

output "api_gateway_free_plan_authorizer_id" {
  value = module.api_gateway_free_plan_authorizer.authorizer_id
}

# output "api_gateway_intermediate_plan_authorizer_id" {
#   value = module.api_gateway_intermediate_plan_authorizer.authorizer_id
# }
#
# output "api_gateway_premium_plan_authorizer_id" {
#   value = module.api_gateway_premium_plan_authorizer.authorizer_id
# }
#
# output "api_gateway_business_partner_authorizer_id" {
#   value = module.api_gateway_business_partner_authorizer.authorizer_id
# }
