# This terraform file hosts the resources directly related to the EC2
# instance used by the API.

data "local_file" "api_nginx_config" {
  filename = "api-configuration/nginx_config.conf"
}

data "local_file" "api_crontab_file" {
  filename = "api-configuration/crontab.txt"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name = "name"
    # This is a HVM, EBS backed SSD Ubuntu LTS AMI
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22*amd64-server*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

}

resource "aws_instance" "api_server_1" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.api_instance_type
  availability_zone      = "${var.region}a"
  vpc_security_group_ids = [aws_security_group.scpca_portal_api.id]
  iam_instance_profile   = aws_iam_instance_profile.scpca_portal_instance_profile.name
  subnet_id              = aws_subnet.scpca_portal_1a.id
  key_name               = aws_key_pair.scpca_portal.key_name
  depends_on = [
    aws_db_instance.postgres_db,
    aws_security_group_rule.scpca_portal_api_http,
    aws_security_group_rule.scpca_portal_api_outbound,
    aws_key_pair.scpca_portal,
    aws_s3_bucket.scpca_portal_cert_bucket
  ]

  user_data = templatefile(
    "api-configuration/api-server-instance-user-data.tpl.sh",
    {
      nginx_config             = data.local_file.api_nginx_config.content
      crontab_file             = data.local_file.api_crontab_file.content
      scpca_portal_cert_bucket = aws_s3_bucket.scpca_portal_cert_bucket.id
      api_environment = templatefile(
        "api-configuration/environment.tpl",
        {
          django_secret_key                     = var.django_secret_key
          database_host                         = aws_db_instance.postgres_db.address
          database_port                         = aws_db_instance.postgres_db.port
          database_user                         = aws_db_instance.postgres_db.username
          database_name                         = aws_db_instance.postgres_db.db_name
          database_password                     = var.database_password
          aws_batch_fargate_job_queue_name      = module.batch.job_queue_name_fargate
          aws_batch_fargate_job_definition_name = module.batch.job_definition_name_fargate
          aws_batch_ec2_job_queue_name          = module.batch.job_queue_name_ec2
          aws_batch_ec2_job_definition_name     = module.batch.job_definition_name_ec2
          aws_region                            = var.region
          aws_s3_bucket_name                    = aws_s3_bucket.scpca_portal_bucket.id
          aws_ses_domain                        = local.ses_domain
          sentry_dsn                            = var.sentry_dsn
          sentry_env                            = var.sentry_env
          slack_ccdl_test_channel_email         = var.slack_ccdl_test_channel_email
          enable_feature_preview                = var.enable_feature_preview
      })
      start_api_with_migrations = templatefile(
        "api-configuration/start_api_with_migrations.tpl.sh",
        {
          region            = var.region
          dockerhub_account = var.dockerhub_account
          log_group         = aws_cloudwatch_log_group.scpca_portal_log_group.name
          log_stream        = aws_cloudwatch_log_stream.log_stream_api.name
      })
      run_command_script = templatefile(
        "api-configuration/run_command.tpl.sh",
        {
          dockerhub_account = var.dockerhub_account
      })
      user   = var.user
      stage  = var.stage
      region = var.region

      log_group                  = aws_cloudwatch_log_group.scpca_portal_log_group.name
      nginx_access_log_stream    = aws_cloudwatch_log_stream.log_stream_api_nginx_access.name
      nginx_error_log_stream     = aws_cloudwatch_log_stream.log_stream_api_nginx_error.name
      sync_batch_jobs_log_stream = aws_cloudwatch_log_stream.log_stream_api_sync_batch_jobs.name
      submit_pending_log_stream  = aws_cloudwatch_log_stream.log_stream_api_submit_pending.name
  })

  tags = merge(
    var.default_tags,
    {
      Name = "ScPCA Portal API ${var.user}-${var.stage}"
    }
  )

  # This should be approx x3.5 of the biggest project's size.
  root_block_device {
    volume_type = "gp3"
    volume_size = 1400
    tags = merge(
      var.default_tags,
      {
        Name = "scpca-block-${var.user}-${var.stage}"
      }
    )
  }
}

output "api_server_1_ip" {
  value = aws_instance.api_server_1.public_ip
}
