resource "aws_batch_job_definition" "generate_computed_files_job" {
  name = "generate-computed-files-job-${var.user}-${var.stage}"
  type = "container"

  platform_capabilities = [
    "FARGATE",
  ]
  container_properties = jsonencode({
    command = ["sportal", "generate-computed-files", "--scpca-id", "<scpca-id>"]
    image   = "ccdl/scpca_portal_api"

    # t2.medium has 2 vcpus and 4.0 GB of RAM
    vcpus  = 2
    memory = 4000
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
