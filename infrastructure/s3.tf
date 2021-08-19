resource "aws_s3_bucket" "scpca_portal_bucket" {
  bucket = "scpca-portal-${var.user}-${var.stage}"
  acl = "private"
  force_destroy = var.stage == "prod" ? false : true

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-${var.user}-${var.stage}"
      Environment = var.stage
    }
  )
}
