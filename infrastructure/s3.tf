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

resource "aws_s3_bucket_public_access_block" "scpca_portal_bucket" {
  bucket = aws_s3_bucket.scpca_portal_bucket.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket" "scpca_portal_cert_bucket" {
  bucket = "scpca-portal-cert-${var.user}-${var.stage}"
  acl = "private"
  force_destroy = var.stage == "prod" ? false : true

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-cert-${var.user}-${var.stage}"
      Environment = var.stage
    }
  )
}

resource "aws_s3_bucket_public_access_block" "scpca_portal_cert_bucket" {
  bucket = aws_s3_bucket.scpca_portal_cert_bucket.id

  block_public_acls   = true
  block_public_policy = true
}
