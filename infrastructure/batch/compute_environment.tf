resource "aws_batch_compute_environment" "scpca_portal_project" {
  compute_environment_name = "scpca-portal-project-compute-${var.user}-${var.stage}"

  compute_resources {
    max_vcpus = 16
    security_group_ids = [
      aws_security_group.scpca_portal_batch.id
    ]

    subnets = [
      var.scpca_portal_subnet_1a.id
    ]

    type = "FARGATE"
  }

  service_role = aws_iam_role.batch_service_role.arn
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.batch_service_role]

  tags = var.batch_tags
}
