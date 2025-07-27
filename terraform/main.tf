
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
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.default.email
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

resource "google_service_account" "default" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}


resource "google_project_iam_member" "aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.default.email}"
}

resource "google_project_iam_member" "storage_object_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.default.email}"
}


resource "google_cloud_run_service_iam_member" "dslans_invoker" {
  location = google_cloud_run_v2_service.default.location
  project  = google_cloud_run_v2_service.default.project
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "user:dslans@gmail.com"
}

resource "google_cloud_run_service_iam_member" "scouvrard_invoker" {
  location = google_cloud_run_v2_service.default.location
  project  = google_cloud_run_v2_service.default.project
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "user:scouvrard@gmail.com"
}

# locals {
#   invoker_users_config = yamldecode(file("${path.module}/auth_users.yaml"))
#   invoker_members      = local.invoker_users_config.invoker_users
# }

# resource "google_cloud_run_service_iam_binding" "invoker_binding" {
#   service  = google_cloud_run_v2_service.default.name
#   location = google_cloud_run_v2_service.default.location
#   role     = "roles/run.invoker"
#   members  = local.invoker_members
# }

