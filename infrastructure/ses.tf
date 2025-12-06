# These do not get destroyed on tear down.
# They get destroyed when the DNS records are removed.
# The DNS records are available in the console.

resource "aws_ses_domain_identity" "scpca_portal" {
  domain = local.ses_domain

  # lifecycle {
  #   prevent_destroy = true
  # }
}

resource "aws_ses_domain_dkim" "scpca_portal" {
  domain = aws_ses_domain_identity.scpca_portal.domain

  # lifecycle {
  #   prevent_destroy = true
  # }
}

resource "aws_ses_domain_mail_from" "scpca_portal" {
  domain                 = aws_ses_domain_identity.scpca_portal.domain
  mail_from_domain       = "mail.${local.ses_domain}"
  behavior_on_mx_failure = "UseDefaultValue"

  # lifecycle {
  #   prevent_destroy = true
  # }
}
