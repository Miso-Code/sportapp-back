resource "google_cloud_run_v2_service" "run_service" {
  name     = var.name
  location = var.location
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      max_instance_count = var.max_instance_count
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [var.env.db_instance]
      }
    }

    service_account = var.service_account

    containers {
      image = var.image
      ports {
        container_port = var.port
      }
      env {
        name  = "DATABASE_URL"
        value = var.env.db_url
      }
      dynamic "env" {
        for_each = var.secrets

        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = "projects/sportapp-417820/secrets/${env.key}"
              version = env.value
            }
          }
        }
      }
      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_binding" "binding" {
  project  = google_cloud_run_v2_service.run_service.project
  location = google_cloud_run_v2_service.run_service.location
  name     = google_cloud_run_v2_service.run_service.name
  role     = "roles/run.invoker"
  members  = [
    "allUsers",
  ]
}
