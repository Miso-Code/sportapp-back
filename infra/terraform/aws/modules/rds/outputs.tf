output "host" {
  description = "URL for accessing the RDS instance"
  value       = aws_db_instance.db.address
}

output "port" {
  description = "Port for accessing the RDS instance"
  value       = aws_db_instance.db.port
}
