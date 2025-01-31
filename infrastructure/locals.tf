locals {
  stage_domains = {
    prod = var.ses_domain,
    staging = "staging.${var.ses_domain}",
    dev = "${var.user}.${var.ses_domain}"
  }

  ses_domain = local.stage_domains[var.stage]
}
