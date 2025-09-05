resource "aws_s3_bucket" "scpca_portal_bucket" {
  bucket = "scpca-portal-${var.user}-${var.stage}"
  force_destroy = var.stage == "prod" ? false : true

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-${var.user}-${var.stage}"
      Environment = var.stage
    }
  )
}

resource "aws_s3_bucket_ownership_controls" "scpca_portal_bucket" {
  bucket = aws_s3_bucket.scpca_portal_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "scpca_portal_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.scpca_portal_bucket]

  bucket = aws_s3_bucket.scpca_portal_bucket.id
  acl = "private"
}

resource "aws_s3_bucket_public_access_block" "scpca_portal_bucket" {
  bucket = aws_s3_bucket.scpca_portal_bucket.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket" "scpca_portal_cert_bucket" {
  bucket = "scpca-portal-cert-${var.user}-${var.stage}"
  force_destroy = var.stage == "prod" ? false : true

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-cert-${var.user}-${var.stage}"
      Environment = var.stage
    }
  )
}

resource "aws_s3_bucket_ownership_controls" "scpca_portal_cert_bucket" {
   bucket = aws_s3_bucket.scpca_portal_cert_bucket.id
   rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "scpca_portal_cert_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.scpca_portal_cert_bucket]
  bucket = aws_s3_bucket.scpca_portal_cert_bucket.id
  acl = "private"
}

 resource "aws_s3_bucket_lifecycle_configuration" "scpca_portal_cert_bucket" {
  bucket = aws_s3_bucket.scpca_portal_cert_bucket.id
  rule {
    id = "auto-delete-after-30-days-${var.user}-${var.stage}"
    filter {}
    status = "Enabled"
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_public_access_block" "scpca_portal_cert_bucket" {
  bucket = aws_s3_bucket.scpca_portal_cert_bucket.id

  block_public_acls   = true
  block_public_policy = true
}

# Static site hosting for cellbrowser iframe on portal
resource "aws_s3_bucket" "scpca_portal_cellbrowser_bucket" {
  bucket = "scpca-portal-cellbrowser-${var.user}-${var.stage}"
}

resource "aws_s3_bucket_acl" "scpca_portal_cellbrowser_bucket" {
  bucket = aws_s3_bucket.scpca_portal_bucket.id
  acl = "public-read"
}

resource "aws_s3_bucket_website_configuration" "scpca_portal_cellbrowser_bucket" {
  bucket = aws_s3_bucket.scpca_portal_cellbrowser_bucket.id

  index_document {
    suffix = "index.html"
  }

  # Optional: specify a custom error page
  # error_document {
  #   key = "error.html"
  # }

  # Optional: Add routing rules if needed
  # routing_rule {
  #   condition {
  #     key_prefix_equals = "images/"
  #   }
  #   redirect {
  #     replace_key_prefix_with = "assets/"
  #   }
  # }
}

resource "aws_s3_bucket_policy" "scpca_portal_cellbrowser_access_policy" {
  bucket = aws_s3_bucket.scpca_portal_cellbrowser_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "PublicReadGetObjectWithCustomHeader"
        Effect = "Allow"
        Principal = "*"
        Action = "s3:GetObject"
        Resource = "${aws_s3_bucket.scpca_portal_cellbrowser_bucket.arn}/*"
        Condition = {
          StringLike = {
              "s3:x-amz-meta-security-token" = [
                var.cellbrowser_security_token
              ]
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_policy" "scpca_portal_cellbrowser_upload_policy" {
  bucket = aws_s3_bucket.scpca_portal_cellbrowser_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ScienceTeamWriteObject"
        Effect = "Allow"
        Principal = {
          "AWS": var.cellbrowser_uploaders
        }
        Action = "s3:PutObject"
        Resource = "${aws_s3_bucket.scpca_portal_cellbrowser_bucket.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "scpca_portal_cellbrowser_bucket" {
  bucket = aws_s3_bucket.scpca_portal_cellbrowser_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

