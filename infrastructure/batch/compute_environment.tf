resource "aws_batch_compute_environment" "scpca_portal_fargate" {
  compute_environment_name = "scpca-portal-fargate-compute-${var.user}-${var.stage}"

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

  lifecycle {
    create_before_destroy = true
  }

  service_role = aws_iam_role.batch_service_role.arn
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.batch_service_role]

  tags = var.batch_tags
}

resource "aws_batch_compute_environment" "scpca_portal_ec2" {
  # Prefix to avoid error on deploy.
  # ClientException: Cannot delete, found existing JobQueue relationship.
  compute_environment_name_prefix = "scpca-portal-ec2-compute-${var.user}-${var.stage}"

  compute_resources {
    type = "EC2"
    max_vcpus = 16
    desired_vcpus = 2
    security_group_ids = [
      aws_security_group.scpca_portal_batch.id
    ]
    subnets = [
      var.scpca_portal_subnet_1a.id
    ]

    # t2.large is the api's instance type but we should decide if we to change it
    instance_type = ["optimal"]
    instance_role = aws_iam_instance_profile.batch_instance_profile.arn

    launch_template {
      launch_template_id = aws_launch_template.scpca_portal_ec2.id
      # The version attr was changed from aws_launch_template.scpca_portal_ec2.latest_version to $Latest
      # because the latest_version attribute kept switching versions unexpectedly in between deploys.
      # This ultimately necessitated the spinning down of the entire stack
      # due to a chicken and egg situation with the compute env and its linked job queue.
      version = "$Latest"
    }

  }

  lifecycle {
    create_before_destroy = true
  }

  service_role = aws_iam_role.batch_service_role.arn
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.batch_service_role]

  tags = var.batch_tags
}

resource "aws_launch_template" "scpca_portal_ec2" {
  name = "scpca-portal-ec2-launch-template-${var.user}-${var.stage}"
  image_id = data.aws_ami.ecs_optimized_amazon_linux.id

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 800
      volume_type = "gp3"
      delete_on_termination = true
    }
  }

  iam_instance_profile {
    name = aws_iam_instance_profile.batch_instance_profile.name
  }

  tag_specifications {
    resource_type = "instance"
    tags = var.batch_tags
  }
}

# aws ami which is ecs optimized for amazon linux
data "aws_ami" "ecs_optimized_amazon_linux" {
  most_recent = true
  owners = ["591542846629"] # ECS team account

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }

}
