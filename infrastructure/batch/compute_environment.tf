resource "aws_batch_compute_environment" "scpca_portal_project" {
  compute_environment_name = "scpca-portal-project-compute-${var.user}-${var.stage}"

  compute_resources {
    type = "FARGATE"
    max_vcpus = 16
    security_group_ids = [
      aws_security_group.scpca_portal_batch.id
    ]

    subnets = [
      var.scpca_portal_subnet_1a.id
    ]

  }

  service_role = aws_iam_role.batch_service_role.arn
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.batch_service_role]

  tags = var.batch_tags
}

resource "aws_batch_compute_environment" "scpca_portal_ec2" {
  compute_environment_name = "scpca-portal-ec2-compute-${var.user}-${var.stage}"

  compute_resources {
    type = "EC2"
    min_vcpus = 0
    max_vcpus = 16
    desired_vcpus = 0
    instance_type = var.instance_type
    security_group_ids = [
      aws_security_group.scpca_portal_batch.id
    ]
    subnets = [
      var.scpca_portal_subnet_1a.id
    ]
    instance_role = aws_iam_role.ec2_instance_profile.arn
    ec2_key_pair = var.ec2_key_name
  }

  service_role = aws_iam_role.batch_service_role.arn
  type         = "MANAGED"
  # depends_on   = [aws_iam_role_policy_attachment.batch_service_role]

  tags = var.batch_tags
}
