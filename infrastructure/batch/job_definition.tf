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
    resourceRequirements = [
      # t2.medium has 2 vcpus and 4.0 GB of RAM
      {
        type = "VCPU"
        value = "2.0"
      },
      {
        type = "MEMORY"
        value = "4096"
      }

    ]

    volumes = [
      {
        host = "efs-volume"
        efsVolumeConfiguration = {
          # fileSystemId = # needs to be configured, will read something like aws_efs_file_system.name.id
        }
      }
    ]
    mountPoints = [
      {
        sourceVolume = "efs-volume"
        # containerPath = path inside container where EFS volume is mounted
      }
    ]
    executionRoleArn = aws_iam_role.aws_ecs_task_execution_role.arn
  })
}
