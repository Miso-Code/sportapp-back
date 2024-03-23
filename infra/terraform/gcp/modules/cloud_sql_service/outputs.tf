output "host" {
  description = "URL for accessing the Cloud SQL instance"
  value       = google_sql_database_instance.instance.public_ip_address
}

output "database_name" {
  description = "Name of the database created"
  value       = google_sql_database.database.name
}

output "instance_connection_name" {
  description = "Connection name for the Cloud SQL instance"
  value       = google_sql_database_instance.instance.connection_name
}
