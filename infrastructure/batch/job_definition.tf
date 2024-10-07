resource "aws_batch_job_definition" "scpca_portal_project" {
  name = "scpca-portal-project-job-definition-${var.user}-${var.stage}"
  type = "container"

  platform_capabilities = [
    "FARGATE",
  ]
  container_properties = jsonencode({
    # command definition expected in cotaninerOverrides when using this job definition
    command = []
    image   = "${var.dockerhub_repo}/scpca_portal_api:latest"
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

    executionRoleArn = aws_iam_role.aws_ecs_task_execution_role.arn
  })
}
