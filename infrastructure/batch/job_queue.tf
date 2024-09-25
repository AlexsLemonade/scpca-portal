resource "aws_batch_job_queue" "scpca_portal_queue" {
  name = "scpca-portal-queue-${var.user}-${var.stage}"
  state = "ENABLED"
  priority = 1

  # compute_environments = [] array is deprecated
  computed_environment_order {
    order = 1
    compute_environment = aws_batch_compute_environments.scpca_portal.arn
  }

  tags = var.default_tags
}
