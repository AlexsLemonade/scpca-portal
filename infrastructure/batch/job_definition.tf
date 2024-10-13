resource "aws_batch_job_definition" "scpca_portal_project" {
  name = "scpca-portal-project-job-definition-${var.user}-${var.stage}"
  type = "container"

  platform_capabilities = [
    "FARGATE",
  ]
  container_properties = jsonencode({
    # command definition expected in cotaninerOverrides when using this job definition
    command = []
    image   = var.batch_image
    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }
    environment = var.batch_environment

    resourceRequirements = var.batch_resource_requirements

    # without this declaration, ephemeralStroage defaults to 20GB
    ephemeralStorage = {
      sizeInGib = 200
    }

    executionRoleArn = aws_iam_role.aws_ecs_task_execution_role.arn
  })
}
