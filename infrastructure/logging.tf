# This terraform file hosts the resources directly related to logging.


# This is the group. All of the streams belong to this.
resource "aws_cloudwatch_log_group" "scpca_portal" {
  name = "scpca-portal-log-group-${var.user}-${var.stage}"

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-log-group-${var.user}-${var.stage}"
    }
  )
}

# Streams
resource "aws_cloudwatch_log_stream" "log_stream_api" {
  name = "log-stream-api-${var.user}-${var.stage}"
  log_group_name = aws_cloudwatch_log_group.scpca_portal.name
}

resource "aws_cloudwatch_log_stream" "log_stream_api_nginx_access" {
  name = "log-stream-api-nginx-access-${var.user}-${var.stage}"
  log_group_name = aws_cloudwatch_log_group.scpca_portal.name
}

resource "aws_cloudwatch_log_stream" "log_stream_api_nginx_error" {
  name = "log-stream-api-nginx-error-${var.user}-${var.stage}"
  log_group_name = aws_cloudwatch_log_group.scpca_portal.name
}
