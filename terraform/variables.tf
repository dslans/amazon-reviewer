variable "project_id" {
  description = "The Google Cloud project ID to deploy to."
  type        = string
}

variable "region" {
  description = "The Google Cloud region to deploy to."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "amazon-reviewer"
}
