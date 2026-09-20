# Account-wide safety net. Credits are left out on purpose: on the Free plan,
# spending credits is what ends the plan early, so that is what should alert.
resource "aws_budgets_budget" "monthly" {
  name         = "account-monthly-cost"
  budget_type  = "COST"
  limit_amount = format("%.1f", var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_types {
    include_credit = false
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.alert_email]
  }
}
