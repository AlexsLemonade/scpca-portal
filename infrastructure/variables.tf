# This terraform file hosts the terraform variables used throughout
# the project.

data "aws_caller_identity" "current" {}

variable "default_tags" {
  default = {
    team    = "engineering"
    project = "ScPCA Portal"
  }
  description = "Default resource tags"
  type        = map(string)
}

variable "region" {
  default = "us-east-1"
}

variable "user" {
  default = "myusername"
}

variable "stage" {
  default = "dev"

  validation {
    condition     = contains(["prod", "staging", "dev"], var.stage)
    error_message = "The environment must be 'prod', 'staging', or 'dev'."
  }
}

variable "dockerhub_account" {
  default = "ccdlstaging"
}

variable "system_version" {
  default = "INVALID SYSTEM VERSION"
}

variable "django_secret_key" {
  # This will be overwritten by the password in GitHub actions.
  # It's kept there so it's secret.
  default = "THIS_IS_NOT_A_SECRET_DO_NOT_USE_IN_PROD"
}

variable "database_password" {
  # This will be overwritten by the password in GitHub actions.
  # It's kept there so it's secret.
  default = "scpcapostgrespassword"
}

variable "database_port" {
  default = "5432"
}

variable "api_instance_type" {
  default = "t2.large"
}

variable "database_instance_type" {
  default = "db.t3.micro"
}

variable "sentry_dsn" {
  default = "MISSING_VALUE"
}

variable "sentry_env" {
  default = "MISSING_VALUE"
}

variable "ssh_public_key" {
  default = "MISSING_VALUE"
}

variable "slack_notifications_email" {
  default = "testing@example.com"
}

variable "enable_feature_preview" {
  default = "false"
}

variable "cellbrowser_security_token" {
  default = "MISSING_VALUE"
}

variable "cellbrowser_uploaders" {
  default = []
  type    = list(string)
}

locals {

  stage_domains = {
    prod    = "scpca.alexslemonade.org"
    staging = "staging.scpca.alexslemonade.org"
    dev     = "dev.scpca.alexslemonade.org"
  }

  ses_domain = local.stage_domains[var.stage]

}

output "environment_variables" {
  value = [
    { name = "DATABASE_NAME"
    value = aws_db_instance.postgres_db.db_name },
    { name = "DATABASE_HOST"
    value = aws_db_instance.postgres_db.address },
    { name = "DATABASE_USER"
    value = aws_db_instance.postgres_db.username },
    { name = "DATABASE_PORT"
    value = aws_db_instance.postgres_db.port }
  ]
}
