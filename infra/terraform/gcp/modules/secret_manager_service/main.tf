resource "google_secret_manager_secret" "secret" {
  secret_id = var.secret_id
  replication {
    auto {}
  }
}