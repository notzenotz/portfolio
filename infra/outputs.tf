output "site_url" {
  description = "Public address of the portfolio."
  value       = "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "site_bucket" {
  description = "GitHub variable S3_BUCKET."
  value       = aws_s3_bucket.site.bucket
}

output "cloudfront_distribution_id" {
  description = "GitHub variable CLOUDFRONT_DISTRIBUTION_ID."
  value       = aws_cloudfront_distribution.site.id
}

output "github_actions_role_arn" {
  description = "GitHub variable AWS_ROLE_ARN."
  value       = aws_iam_role.github_deploy.arn
}
