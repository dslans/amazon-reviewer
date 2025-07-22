
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.28.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
}

## Uses existisng repository
# data "google_artifact_registry_repository" "registry" {
#   location      = var.region
#   repository_id = "mcp-cloud-run-deployments"
# }

resource "google_artifact_registry_repository" "registry" {
  location      = var.region
  repository_id = "${var.service_name}-repo"
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "default" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = "us-central1-docker.pkg.dev/agent-smith-3/amazon-product-reviewer-repo/amazon-product-reviewer:latest"
      ports {
        container_port = 8501
      }
      startup_probe {
        http_get {
          port = 8501
        }
      }
    }
  }

  deletion_protection = false

  depends_on = [google_project_service.run_api]
}

resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.default.location
  project  = google_cloud_run_v2_service.default.project
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
