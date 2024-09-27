resource "aws_batch_job_definition" "scpca_portal_project" {
  name = "scpca-portal-project-job-definition-${var.user}-${var.stage}"
  type = "container"

  platform_capabilities = [
    "FARGATE",
  ]
  container_properties = jsonencode({
    # get command right
    command = ["sportal", "generate-computed-files", "--scpca-id", "<scpca-id>"]
    image   = "ccdl/scpca_portal_api"
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

    # this only works with tf version >= 5.12.0
    # without this declaration, ephemeralStroage defaults to 20GB
    ephemeralStorage = {
      sizeInGib = 200
    }

    executionRoleArn = aws_iam_role.aws_ecs_task_execution_role.arn
  })
}
