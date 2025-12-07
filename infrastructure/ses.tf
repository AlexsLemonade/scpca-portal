# NOTE: The following SES resources were created with terraform.
# However, in order to support multiple dev stacks,
# after the initial deploy we follow up with another deploy that
# removes these resources from being tracked in the state file.

# The below comment shows how they were created,
# their state may have changed since.

# resource "aws_ses_domain_identity" "scpca_portal" {
#   domain = local.ses_domain
# }

# resource "aws_ses_domain_dkim" "scpca_portal" {
#   domain = aws_ses_domain_identity.scpca_portal.domain
# }

# resource "aws_ses_domain_mail_from" "scpca_portal" {
#   domain                 = aws_ses_domain_identity.scpca_portal.domain
#   mail_from_domain       = "mail.${local.ses_domain}"
#   behavior_on_mx_failure = "UseDefaultValue"
# }

data "aws_ses_domain_identity" "scpca_portal" {
  domain = local.ses_domain
}

removed {
  from = aws_ses_domain_identity.scpca_portal

  lifecycle {
    destroy = false
  }
}

removed {
  from = aws_ses_domain_dkim.scpca_portal

  lifecycle {
    destroy = false
  }
}

removed {
  from = aws_ses_domain_mail_from.scpca_portal

  lifecycle {
    destroy = false
  }
}
