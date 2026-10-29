resource "aws_s3_bucket" "scpca_portal_bucket" {
  bucket        = "scpca-portal-${var.user}-${var.stage}"
  force_destroy = var.stage == "prod" ? false : true

  tags = merge(
    var.default_tags,
    {
      Name        = "scpca-portal-${var.user}-${var.stage}"
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
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "scpca_portal_bucket" {
  bucket = aws_s3_bucket.scpca_portal_bucket.id

  block_public_acls   = true
  block_public_policy = true
}

# AWS runs the Lifecycle rule at 00:00 UTC daily, so the expiration is
# set to 7+1 days to provide a buffer for the portal UI
resource "aws_s3_bucket_lifecycle_configuration" "scpca_portal_bucket" {
  bucket = aws_s3_bucket.scpca_portal_bucket.id

  rule {
    id     = "expire-user-dataset-${var.user}-${var.stage}"
    status = "Enabled"
    filter {
      tag {
        key   = "dataset_type"
        value = "user"
      }
    }
    expiration {
      days = 8
    }
  }
}

# Input bucket holding the data the API and Batch load from.
# Prod holds released data; staging holds released and unreleased data.
resource "aws_s3_bucket" "scpca_portal_input_bucket" {
  bucket = "scpca-portal-input-${var.user}-${var.stage}"

  tags = merge(
    var.default_tags,
    {
      Name        = "scpca-portal-input-${var.user}-${var.stage}"
      Environment = var.stage
    }
  )

  # The data is costly to lose
  lifecycle {
    prevent_destroy = true
  }
}

# BucketOwnerEnforced disables ACLs, so the portal account owns (and can read)
# every object the science team uploads
resource "aws_s3_bucket_ownership_controls" "scpca_portal_input_bucket" {
  bucket = aws_s3_bucket.scpca_portal_input_bucket.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "scpca_portal_input_bucket" {
  bucket = aws_s3_bucket.scpca_portal_input_bucket.id

  block_public_acls   = true
  block_public_policy = true
}

# TODO: do we want server side encryption for input bucket files?
# resource "aws_s3_bucket_server_side_encryption_configuration" "scpca_portal_input_bucket" {
#   bucket = aws_s3_bucket.scpca_portal_input_bucket.id
#
#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"
#     }
#     bucket_key_enabled = true
#   }
# }

# TODO: confirm science access policy and mechanism
# resource "aws_s3_bucket_policy" "scpca_portal_input_bucket_science_access" {
#   bucket = aws_s3_bucket.scpca_portal_input_bucket.id
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid    = "InputBucketScienceAccess"
#         Effect = "Allow"
#         Principal = {
#           # Figure out exact mechanism to pass through uploaders
#           "AWS" : var.input_bucket_uploaders
#         }
#         Action = [
#           "s3:GetObject",
#           "s3:PutObject",
#           "s3:PutObjectTagging",
#           "s3:DeleteObject",
#           "s3:ListBucket",
#         ]
#         Resource = [
#           "${aws_s3_bucket.scpca_portal_input_bucket.arn}",
#           "${aws_s3_bucket.scpca_portal_input_bucket.arn}/*"
#         ]
#       }
#     ]
#   })
# }

resource "aws_s3_bucket" "scpca_portal_cert_bucket" {
  bucket        = "scpca-portal-cert-${var.user}-${var.stage}"
  force_destroy = var.stage == "prod" ? false : true

  tags = merge(
    var.default_tags,
    {
      Name        = "scpca-portal-cert-${var.user}-${var.stage}"
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
  bucket     = aws_s3_bucket.scpca_portal_cert_bucket.id
  acl        = "private"
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

resource "aws_s3_bucket_policy" "scpca_portal_cellbrowser_bucket_policy" {
  bucket = aws_s3_bucket.scpca_portal_cellbrowser_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ScienceTeamWriteObject"
        Effect = "Allow"
        Principal = {
          "AWS" : var.cellbrowser_uploaders
        }
        Action = [
          "s3:DeleteObject",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject",
          "s3:PutObjectTagging"
        ]
        Resource = [
          "${aws_s3_bucket.scpca_portal_cellbrowser_bucket.arn}",
          "${aws_s3_bucket.scpca_portal_cellbrowser_bucket.arn}/*"
        ]
      },
      {
        Sid       = "PublicReadGetObjectWithSecretHeader"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.scpca_portal_cellbrowser_bucket.arn}/*"
        Condition = {
          StringEquals = {
            "aws:Referer" = var.cellbrowser_security_token
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "scpca_portal_cellbrowser_bucket" {
  bucket = aws_s3_bucket.scpca_portal_cellbrowser_bucket.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

resource "aws_s3_bucket_cors_configuration" "scpca_portal_cellbrowser_cors_configuration" {
  bucket = aws_s3_bucket.scpca_portal_cellbrowser_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = []
    max_age_seconds = 3000
  }
}
