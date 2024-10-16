resource "aws_iam_role" "batch_service_role" {
  name               = "scpca-portal-batch-service-role-${var.user}-${var.stage}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
  {
    "Action": "sts:AssumeRole",
    "Effect": "Allow",
    "Principal": {
      "Service": "batch.amazonaws.com",
    }
  }
  ]
}
EOF
  tags               = var.default_tags
}

resource "aws_iam_role_policy_attachment" "batch_service_role" {
  role       = aws_iam_role.batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "scpca-portal-ecs-task-role-${var.user}-${var.stage}"

  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      }
    }
    ]
 }
 EOF

  tags = var.default_tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "ecs_task_s3_access_policy" {
  name = "scpca-portal-ecs-task-s3-access-${var.user}-${var.stage}"

  policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
    {
      "Effect": "Allow",
      "Action": [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::scpca-portal-inputs",
        "arn:aws:s3:::scpca-portal-inputs/*",
        # s3 output bucket should be added dynamically at runtime
        "arn:aws:s3:::${var.AWS_S3_OUTPUT_BUCKET_NAME}",
        "arn:aws:s3:::${var.AWS_S3_OUTPUT_BUCKET_NAME}/*",
      ]
    }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3_access_policy_attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_s3_access_policy.arn
}
