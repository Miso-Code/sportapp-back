provider "google" {
  project     = "sportapp-417820"
  region      = "us-central1"
}

data "google_secret_manager_secret_version" "db_username" {
  secret = "projects/480619174578/secrets/DB_USERNAME"
}

data "google_secret_manager_secret_version" "db_password" {
  secret = "projects/480619174578/secrets/DB_PASSWORD"
}

module "db" {
  source        = "../modules/cloud_sql_service"
  region        = "us-central1"
  database_name = "sportapp"
  instance_name = "sportapp"
  password      = data.google_secret_manager_secret_version.db_password.secret_data
  username      = data.google_secret_manager_secret_version.db_username.secret_data
}
