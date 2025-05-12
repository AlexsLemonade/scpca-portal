resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "scpca-portal-ec2-instance-profile-${var.user}-${var.stage}"
  role = aws_iam_role.ec2_instance_role.name
}

resource "aws_iam_role" "ec2_instance_role" {
  name = "scpca-portal-ec2-instance-role-${var.user}-${var.stage}"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role_policy.json
}

data "aws_iam_policy_document" "ec2_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}
