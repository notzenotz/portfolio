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
