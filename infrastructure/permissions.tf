# The configuration contained in this file specifies AWS IAM roles and
# permissions.

resource "aws_iam_role" "scpca_portal_instance" {
  name = "scpca-portal-instance-${var.user}-${var.stage}"

  # Policy text found at:
  # http://docs.aws.amazon.com/AmazonECS/latest/developerguide/instance_IAM_role.html
  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": ["ec2.amazonaws.com"]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_instance_profile" "scpca_portal_instance_profile" {
  name = "scpca-portal-instance-profile-${var.user}-${var.stage}"
  role = aws_iam_role.scpca_portal_instance.name
}

resource "aws_iam_policy" "scpca_portal_cloudwatch" {
  name        = "scpca-portal-cloudwatch-policy-${var.user}-${var.stage}"
  description = "Allows Cloudwatch Permissions."


  # Policy text found at:
  # http://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/iam-identity-based-access-control-cwl.html

  # Log streams are created dynamically by Nomad, so we give permission to the entire group
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics",
                "cloudwatch:PutMetricAlarm",
                "cloudwatch:PutMetricData",
                "cloudwatch:SetAlarmState"
            ],
            "Resource": [
              "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.scpca_portal_log_group.name}:*"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.scpca_portal_instance.name
  policy_arn = aws_iam_policy.scpca_portal_cloudwatch.arn
}

resource "aws_iam_policy" "s3_access_policy" {
  name        = "scpca-portal-s3-access-policy-${var.user}-${var.stage}"
  description = "Allows S3 Permissions."

  # Policy text based off of:
  # http://docs.aws.amazon.com/AmazonS3/latest/dev/example-bucket-policies.html
  policy = <<EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "s3:ListAllMyBuckets"
         ],
         "Resource":"arn:aws:s3:::*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:ListBucket",
            "s3:GetBucketLocation"
         ],
         "Resource": [
            "arn:aws:s3:::${aws_s3_bucket.scpca_portal_bucket.bucket}",
            "arn:aws:s3:::${aws_s3_bucket.scpca_portal_cert_bucket.bucket}"
         ]
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject"
         ],
          "Resource": [
            "arn:aws:s3:::${aws_s3_bucket.scpca_portal_bucket.bucket}/*",
            "arn:aws:s3:::${aws_s3_bucket.scpca_portal_cert_bucket.bucket}/*"
          ]
      }
   ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "s3" {
  role       = aws_iam_role.scpca_portal_instance.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

resource "aws_iam_policy" "input_bucket_access_policy" {
  name        = "scpca-portal-input-bucket-access-policy-${var.user}-${var.stage}"
  description = "Allows S3 Permissions to the input bucket."

  policy = <<EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "s3:ListAllMyBuckets"
         ],
         "Resource":"arn:aws:s3:::*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:ListBucket",
            "s3:GetBucketLocation"
         ],
         "Resource":"arn:aws:s3:::scpca-portal-inputs"
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:GetObject"
         ],
          "Resource": [
            "arn:aws:s3:::scpca-portal-inputs/*"
          ]
      }
   ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "input_bucket" {
  role       = aws_iam_role.scpca_portal_instance.name
  policy_arn = aws_iam_policy.input_bucket_access_policy.arn
}

resource "aws_iam_policy" "batch" {
  name = "scpca-portal-batch-submit-job-${var.user}-${var.stage}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "batch:SubmitJob",
        "batch:DescribeJobs"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "batch" {
  role       = aws_iam_role.scpca_portal_instance.name
  policy_arn = aws_iam_policy.batch.arn
}

resource "aws_iam_policy" "api_ses_send_email" {
  name   = "scpca-portal-api-ses-send-email-${var.user}-${var.stage}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:identity/${local.ses_domain}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "api_ses_send_policy" {
  role       = aws_iam_role.scpca_portal_instance.name
  policy_arn = aws_iam_policy.api_ses_send_email.arn
}
