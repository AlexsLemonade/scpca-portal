resource "aws_ses_domain_identity" "scpca_portal" {
  domain = local.ses_domain
}

resource "aws_ses_domain_dkim" "scpca_portal" {
  domain = aws_ses_domain_identity.scpca_portal.domain
}
