resource "aws_db_instance" "db" {
  db_name             = var.database_name
  identifier          = var.database_name
  allocated_storage   = 10
  engine              = "postgres"
  instance_class      = var.instance_class
  username            = var.username
  password            = var.password
  skip_final_snapshot = true
}