resource "aws_batch_job_definition" "scpca_portal_project" {
  name = "scpca-portal-project-job-definition-${var.user}-${var.stage}"
  type = "container"

  platform_capabilities = [
    "FARGATE",
  ]
  container_properties = jsonencode({
    image = "${var.dockerhub_account}/scpca_portal_api:latest"
    # command definition expected in cotaninerOverrides when using this job definition
    command = []
    environment = [
      {
        name  = "DJANGO_CONFIGURATION"
        value = "Production"
      },
      {
        name  = "DJANGO_DEBUG"
        value = false
      },
      {
        name  = "DJANGO_SECRET_KEY"
        value = var.django_secret_key
      },
      {
        name  = "DATABASE_HOST"
        value = aws_db_instance.postgres_db.address
      },
      {
        name  = "DATABASE_PORT"
        value = aws_db_instance.postgres_db.port
      },
      {
        name  = "DATABASE_USER"
        value = aws_db_instance.postgres_db.username
      },
      {
        name  = "DATABASE_NAME"
        value = aws_db_instance.postgres_db.name
      },
      {
        name  = "DATABASE_PASSWORD"
        value = var.database_password
      },
      {
        name  = "AWS_REGION"
        value = var.region
      },
      {
        name  = "AWS_S3_BUCKET_NAME"
        value = aws_s3_bucket.scpca_portal_bucket.id
      },
      {
        name  = "SENTRY_DSN"
        value = var.sentry_dsn
      },
      {
        name  = "SENTRY_ENV"
        value = "${var.stage}-batch"
      }
    ]

    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }
    resourceRequirements = [
      # requirements match api requirements, which uses a t2.medium (2 vcpus and 4.0 GB of RAM)
      {
        type  = "VCPU"
        value = "2.0"
      },
      {
        type  = "MEMORY"
        value = "4096"
      }
    ]
    # without this declaration, ephemeralStroage defaults to 20GB
    ephemeralStorage = {
      sizeInGib = 200
    }

    retry_strategy = {
      attempts = 3
    }

    executionRoleArn = aws_iam_role.aws_ecs_task_execution_role.arn
  })
}
