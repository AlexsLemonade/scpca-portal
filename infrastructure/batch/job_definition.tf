locals {
  job_image = {
    image = "${var.dockerhub_account}/scpca_portal_api:latest"
  }
}

locals {
  job_command = {
    command = []
  }
}

locals {
  job_environment = {
    environment = [
      {
        name  = "DJANGO_CONFIGURATION"
        value = "Production"
      },
      {
        name  = "DJANGO_DEBUG"
        value = "false"
      },
      {
        name  = "DATABASE_HOST"
        value = var.postgres_db.address
      },
      {
        name  = "DATABASE_PORT"
        value = tostring(var.postgres_db.port)
      },
      {
        name  = "DATABASE_USER"
        value = var.postgres_db.username
      },
      {
        name  = "DATABASE_NAME"
        value = var.postgres_db.db_name
      },
      {
        name  = "AWS_REGION"
        value = var.region
      },
      {
        name  = "AWS_S3_BUCKET_NAME"
        value = var.scpca_portal_bucket.bucket
      },
      {
        name  = "SENTRY_ENV"
        value = "${var.stage}-batch"
      },
      {
        name  = "AWS_SES_DOMAIN",
        value = var.aws_ses_domain_identity_scpca_portal.domain
      },
      {
        name  = "SLACK_NOTIFICATIONS_EMAIL",
        value = var.slack_notifications_email
      }
    ]
  }
}

locals {
  job_secrets = {
    # command definition expected in cotaninerOverrides when using this job definition
    secrets = [
      {
        name      = "DJANGO_SECRET_KEY",
        valueFrom = "${var.django_secret_key.arn}"
      },
      {
        name      = "DATABASE_PASSWORD",
        valueFrom = "${var.database_password.arn}"
      },
      {
        name      = "SENTRY_DSN"
        valueFrom = "${var.sentry_dsn.arn}"
      },
    ]
  }
}

locals {
  job_resource_requirements = {
    # requirements match api requirements, which uses a t2.medium (2 vcpus and 4.0 GB of RAM)
    resourceRequirements = [
      {
        type  = "VCPU"
        value = "1"
      },
      {
        type  = "MEMORY"
        value = "4096"
      }
    ]
  }
}

locals {
  job_role_arns = {
    executionRoleArn = aws_iam_role.ecs_task_role.arn
    jobRoleArn       = aws_iam_role.batch_job_role.arn
  }
}

resource "aws_batch_job_definition" "scpca_portal_fargate" {
  name = "scpca-portal-fargate-job-definition-${var.user}-${var.stage}"
  type = "container"

  platform_capabilities = ["FARGATE"]
  container_properties = jsonencode(merge(
    local.job_image,
    local.job_command,
    local.job_environment,
    local.job_secrets,
    local.job_resource_requirements,
    local.job_role_arns,
    {
      # this gives the job outbound network access so that it can pull an image from an external container registry
      networkConfiguration = {
        assignPublicIp = "ENABLED"
      }
      fargatePlatformConfiguration = {
        platformVersion = "LATEST"
      }
      # without this declaration, ephemeralStroage defaults to 20GB
      ephemeralStorage = {
        sizeInGib = 200
      }
    }
  ))

  retry_strategy {
    attempts = 3
  }

  propagate_tags = true
  tags           = var.batch_tags
}

resource "aws_batch_job_definition" "scpca_portal_ec2" {
  name = "scpca-portal-ec2-job-definition-${var.user}-${var.stage}"
  type = "container"

  platform_capabilities = ["EC2"]

  container_properties = jsonencode(merge(
    local.job_image,
    local.job_command,
    local.job_environment,
    local.job_secrets,
    local.job_resource_requirements,
    local.job_role_arns,
    )
  )

  retry_strategy {
    attempts = 3
  }

  propagate_tags = true
  tags           = var.batch_tags
}
