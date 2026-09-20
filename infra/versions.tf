terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # State lives in an S3 bucket created once by hand (see the guide).
  # A backend block cannot read variables, so the bucket name is passed at
  # init time:  terraform init -backend-config="bucket=<state bucket>"
  # use_lockfile gives state locking without a DynamoDB table.
  backend "s3" {
    key          = "portfolio/terraform.tfstate"
    region       = "ap-southeast-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "portfolio"
      ManagedBy = "terraform"
      Repo      = "${var.github_owner}/${var.github_repo}"
    }
  }
}

data "aws_caller_identity" "current" {}

locals {
  # S3 bucket names are global and lowercase, so the account ID keeps ours unique
  slug = trim(replace(lower(var.github_repo), "/[^a-z0-9-]+/", "-"), "-")
  name = "${local.slug}-${data.aws_caller_identity.current.account_id}"
}
