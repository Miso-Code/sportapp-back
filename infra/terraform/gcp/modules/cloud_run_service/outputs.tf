output "service_name" {
  description = "The name of the Cloud Run service"
  value       = google_cloud_run_v2_service.run_service.name
}

output "service_location" {
  description = "The location of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.run_service.location
}

output "service_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.run_service.uri
}
