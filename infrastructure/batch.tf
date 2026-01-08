module "batch" {
  source = "./batch"

  # networking
  scpca_portal_vpc       = aws_vpc.scpca_portal_vpc
  scpca_portal_subnet_1a = aws_subnet.scpca_portal_1a

  # job_definition envars
  dockerhub_account         = var.dockerhub_account
  region                    = var.region
  scpca_portal_bucket       = aws_s3_bucket.scpca_portal_bucket
  postgres_db               = aws_db_instance.postgres_db
  slack_notifications_email = var.slack_notifications_email

  # job_definition secret envars
  django_secret_key = aws_secretsmanager_secret.django_secret_key
  database_password = aws_secretsmanager_secret.database_password
  sentry_dsn        = aws_secretsmanager_secret.sentry_dsn

  # security
  scpca_portal_db_security_group = aws_security_group.scpca_portal_db

  # ses
  aws_ses_domain_identity_scpca_portal = data.aws_ses_domain_identity.scpca_portal

  # general configuration
  aws_caller_identity_current = data.aws_caller_identity.current
  user                        = var.user
  stage                       = var.stage
  batch_tags = {
    module   = "batch",
    revision = "first - 16 vCPU compute environment with 1 vCPU per job"
  }
}
