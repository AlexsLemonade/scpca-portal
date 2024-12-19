resource "aws_batch_job_queue" "scpca_portal_project" {
  name     = "scpca-portal-project-queue-${var.user}-${var.stage}"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order = 1
    compute_environment = aws_batch_compute_environment.scpca_portal_project.arn
  }

  tags = var.batch_tags
}
