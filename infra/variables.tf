variable "aws_region" {
  description = "Region of the S3 bucket. CloudFront itself is global."
  type        = string
  default     = "ap-southeast-1"
}

variable "github_owner" {
  description = "GitHub username that owns the repository."
  type        = string
}

variable "github_repo" {
  description = "Repository name. Only pushes to its main branch are allowed to deploy."
  type        = string
  default     = "portfolio"
}

# Repos created after 15 July 2026 get OIDC subject claims that carry these IDs.
# Get both with: gh api repos/OWNER/REPO --jq ".owner.id, .id"
variable "github_owner_id" {
  description = "Numeric ID of the GitHub account that owns the repository."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.github_owner_id))
    error_message = "github_owner_id harus berupa angka. Ambil dengan: gh api repos/OWNER/REPO --jq .owner.id"
  }
}

variable "github_repo_id" {
  description = "Numeric ID of the repository."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.github_repo_id))
    error_message = "github_repo_id harus berupa angka. Ambil dengan: gh api repos/OWNER/REPO --jq .id"
  }
}

variable "alert_email" {
  description = "Address that receives the monthly budget alerts."
  type        = string

  validation {
    condition     = can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.alert_email))
    error_message = "Isi alert_email di terraform.tfvars dengan alamat email yang valid."
  }
}

variable "monthly_budget_usd" {
  description = "Monthly spend (USD, before credits) that triggers an alert email."
  type        = number
  default     = 5
}
