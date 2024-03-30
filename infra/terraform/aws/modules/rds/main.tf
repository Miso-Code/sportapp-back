resource "aws_db_subnet_group" "subnet_group" {
  name       = "main"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "My DB subnet group"
  }
}

resource "aws_db_instance" "db" {
  db_name                = var.database_name
  identifier             = var.database_name
  allocated_storage      = 10
  engine                 = "postgres"
  instance_class         = var.instance_class
  username               = var.username
  password               = var.password
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.subnet_group.name
}