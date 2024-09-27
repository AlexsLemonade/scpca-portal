resource "aws_batch_compute_environment" "scpca_portal_project_compute" {
  compute_environment_name = "scpca-portal-project-compute-${var.user}-${var.stage}"

  compute_resources {
    max_vcpus = 32
    security_group_ids = [
        aws_security_group.scpca_portal_batch.id
    ]

    subnets = [
        aws_subnet.scpca_portal_1a
    ]

    type = "FARGATE"
  }

  service_role = aws_iam_role.batch_service_role.arn
  type = "MANAGED"
  depends_on = [aws_iam_role_policy_attachment.batch_service_role]

  tags = var.default_tags
}
