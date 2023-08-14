resource "google_cloud_run_v2_service" "default" {
  name     = "my-chroma-api"
  location = var.zone
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
      containers {
        image = "gcr.io/${var.project_id}/my-fastapi-app"

#        env {
#          name = "MY_SECRET_KEY"
#          value_from {
#            secret_key_ref {
#              name = "MY_SECRET_KEY"
#              key  = "latest"
#            }
#          }
#        }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.default.name
  location = google_cloud_run_service.default.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}