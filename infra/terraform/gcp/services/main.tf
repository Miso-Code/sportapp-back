provider "google" {
  project     = "sportapp-417820"
  region      = "us-central1"
  credentials = "../../../../gcloud-credentials.json"
}

data "google_secret_manager_secret_version" "db_username" {
  secret = "projects/480619174578/secrets/DB_USERNAME"
}

data "google_secret_manager_secret_version" "db_password" {
  secret = "projects/480619174578/secrets/DB_PASSWORD"
}

data "google_service_account" "develop_service_account" {
  account_id = "develop"
}

data "terraform_remote_state" "resources" {
  backend = "local"
  config  = {
    path = "../resources/terraform.tfstate"
  }
}

module "users_service" {
  source          = "../modules/cloud_run_service"
  name            = "users-service"
  location        = "us-central1"
  image           = "us-central1-docker.pkg.dev/sportapp-417820/sportapp/users:latest"
  service_account = data.google_service_account.develop_service_account.email
  port            = 8000
  env             = {
    db_url      = "postgresql+psycopg2://${data.google_secret_manager_secret_version.db_username.secret_data}:${data.google_secret_manager_secret_version.db_password.secret_data}@/${data.terraform_remote_state.resources.outputs.database_name}?host=/cloudsql/${data.terraform_remote_state.resources.outputs.instance_connection_name}",
    db_instance = data.terraform_remote_state.resources.outputs.instance_connection_name
  }

  depends_on = [data.terraform_remote_state.resources]
}
