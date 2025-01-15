locals {
  stage_domains = {
    prod = var.ses_domain,
    staging = "staging.${var.ses_domain}",
    dev = "${var.user}.${var.ses_domain}"
  }

  ses_domain = local.stage_domains[var.stage]
}

resource "aws_ses_domain_identity" "scpca_portal" {
  domain = local.ses_domain
}

resource "aws_ses_domain_dkim" "scpca_portal" {
  domain = aws_ses_domain_identity.scpca_portal.domain
}
