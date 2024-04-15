resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.instance.name
}

resource "google_sql_database_instance" "instance" {
  name             = var.instance_name
  region           = var.region
  database_version = var.database_version

  settings {
    tier = var.tier
  }

  deletion_protection = var.deletion_protection
}

resource "google_sql_user" "users" {
  name     = var.username
  password = var.password
  instance = google_sql_database_instance.instance.name
}
