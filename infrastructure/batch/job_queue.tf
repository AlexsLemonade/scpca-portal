resource "aws_batch_job_queue" "scpca_portal_project" {
  name     = "scpca-portal-project-queue-${var.user}-${var.stage}"
  state    = "ENABLED"
  priority = 1

  # compute_environments = [] array is deprecated
  compute_environments = [
    aws_batch_compute_environment.scpca_portal_project.arn,
  ]
  # compute_environment_order {
  #   order               = 1
  #   compute_environment = aws_batch_compute_environments.scpca_portal_project.arn
  # }

  tags = var.default_tags
}
