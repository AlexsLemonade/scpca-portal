 module "batch" {
   source = "./batch"

  # networking
  scpca_portal_vpc = aws_vpc.scpca_portal_vpc
  scpca_portal_subnet_1a = aws_subnet.scpca_portal_1a

  # job_definition envars
  dockerhub_account = var.dockerhub_account
  django_secret_key = var.django_secret_key
  database_password = var.database_password
  region = var.region
  scpca_portal_bucket = aws_s3_bucket.scpca_portal_bucket
  sentry_dsn = var.sentry_dsn
  postgres_db = aws_db_instance.postgres_db

  # security
  scpca_portal_db_security_group = aws_security_group.scpca_portal_db

  # general configuration
  user = var.user
  stage = var.stage
  batch_tags = {
    module = "batch",
    revision = "initial - 16 vCPU compute environment and 1 queue"
  }
}
