resource "aws_s3_bucket" "scpca_portal_bucket" {
  bucket = "scpca-portal-${var.user}-${var.stage}"
  # TODO: remove this when upgrading aws_provider version
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

# TODO: enable after upgrade
# resource "aws_s3_bucket_ownership_controls" "scpca_portal_bucket" {
#  bucket = aws_s3_bucket.scpca_portal_bucket.id
#  rule {
#    object_ownership = "BucketOwnerPreferred"
#  }
#}

# TODO: enable after upgrade
# resource "aws_s3_bucket_acl" "scpca_portal_bucket" {
#  depends_on = [aws_s3_bucket_ownership_controls.scpca_portal_bucket]
#
#  bucket = aws_s3_bucket.scpca_portal_bucket.id
#  acl = "private"
#}

resource "aws_s3_bucket_public_access_block" "scpca_portal_bucket" {
  bucket = aws_s3_bucket.scpca_portal_bucket.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket" "scpca_portal_cert_bucket" {
  bucket = "scpca-portal-cert-${var.user}-${var.stage}"
  # TODO: remove this when upgrading aws_provider version
  acl = "private"
  force_destroy = var.stage == "prod" ? false : true

  # TODO: remove lifecycle rule when we upgrade aws_provider version
  lifecycle_rule {
    id = "auto-delete-after-30-days-${var.user}-${var.stage}"
    prefix = ""
    enabled = true
    abort_incomplete_multipart_upload_days = 1

    expiration {
      days = 30
    }
  }

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-cert-${var.user}-${var.stage}"
      Environment = var.stage
    }
  )
}

# TODO: enable after upgrade
# resource "aws_s3_bucket_ownership_controls" "scpca_portal_cert_bucket" {
#   bucket = aws_s3_bucket.scpca_portal_cert_bucket.id
#   rule {
#    object_ownership = "BucketOwnerPreferred"
#  }
#}

# resource "aws_s3_bucket_acl" "scpca_portal_cert_bucket" {
#  depends_on = [aws_s3_bucket_ownership_controls.scpca_portal_cert_bucket]
#  bucket = aws_s3_bucket.scpca_portal_cert_bucket.id
#  acl = "private"
#}

# resource "aws_s3_bucket_lifecycle_configuration" "scpca_portal_cert_bucket" {
#  bucket = aws_s3_bucket.scpca_portal_cert_bucket.id
#  rule {
#    id = "auto-delete-after-30-days-${var.user}-${var.stage}"
#    status = "Enabled"
#    abort_incomplete_multipart_upload {
#      days_after_initiation = 1
#    }
#
#    expiration {
#      days = 30
#    }
#  }
#}

resource "aws_s3_bucket_public_access_block" "scpca_portal_cert_bucket" {
  bucket = aws_s3_bucket.scpca_portal_cert_bucket.id

  block_public_acls   = true
  block_public_policy = true
}
