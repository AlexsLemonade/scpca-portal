resource "aws_batch_job_queue" "scpca_portal_fargate" {
  name     = "scpca-portal-fargate-queue-${var.user}-${var.stage}"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order = 1
    compute_environment = aws_batch_compute_environment.scpca_portal_fargate.arn
  }

  tags = var.batch_tags
}

resource "aws_batch_job_queue" "scpca_portal_ec2" {
  name     = "scpca-portal-ec2-queue-${var.user}-${var.stage}"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order = 1
    compute_environment = aws_batch_compute_environment.scpca_portal_ec2.arn
  }

  tags = var.batch_tags
}
