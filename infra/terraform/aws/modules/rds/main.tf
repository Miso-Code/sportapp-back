resource "aws_db_subnet_group" "subnet_group" {
  name       = "${var.environment}main"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "My DB subnet group for ${var.environment} environment"
  }
}

resource "aws_db_instance" "db" {
  db_name              = "${var.database_name}${var.environment}"
  identifier           = "${var.database_name}${var.environment}"
  allocated_storage    = 10
  engine               = "postgres"
  instance_class       = var.instance_class
  username             = var.username
  password             = var.password
  skip_final_snapshot  = true
  db_subnet_group_name = aws_db_subnet_group.subnet_group.name
}
