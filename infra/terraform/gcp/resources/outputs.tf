output "instance_connection_name" {
  description = "The connection name for the Cloud SQL instance"
  value       = module.db.instance_connection_name
}

output "database_name" {
  description = "The name of the Cloud SQL database"
  value       = module.db.database_name
}