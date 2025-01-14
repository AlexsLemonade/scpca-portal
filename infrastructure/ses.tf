locals {
  base_domain = "scpca.alexslemonade.org"

  ses_domain = (
    var.stage == "prod" ? local.base_domain :
    var.stage == "staging" ? "staging.${local.base_domain}" :
    "${var.user}.${local.base_domain}"
  )
}

resource "aws_ses_domain_identity" "scpca_portal" {
  domain = local.ses_domain
}

resource "aws_ses_domain_dkim" "scpca_portal" {
  domain = aws_ses_domain_identity.scpca_portal.domain
}
