# This terraform file hosts the resources directly related to security.


resource "aws_key_pair" "scpca_portal" {
  key_name = "scpca-portal-key-${var.user}-${var.stage}"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC88PxkLQUid6nC+8zXSK8jjJ2pe0yIrL5VQnSR1nIWNxCKPmP2xabWlTKvLjMKd6oEROJLC0GlMN17NIKHek0y9dp4wyBawMpJumdkKbmpEnWfpJN5rVuC/G+NPX8FgkAaaJ2M0D6I672D/tiTJ5G0SS8yLG4gWzW0kdFgT3dFchFRelOIOUUC1PwEnbBC186Bbbd7ozuwOSaLNrWw3RsR+pfjYE12PHLRv1H+ePmM0YhNOd6ogdNll1yzjM/jSvSqHNNJekhNQtnmrQ6haS7BaDDTsu5hA5M14SaZDRmv+XT5YGpBD4g5GkikX4HPqR/Ai3OQsm+qQYuBxDWhdx8hSj9LHuRPuhi8DUwBDVptpHeuuWMOYjvmHhI/t2U+8awIy/a0VlCwx5C6J57/XcLkiUbvWmRhpsz5YfWjCMvn1K2uUAE2hP6C8Mdjz2TL94nEf0DL1yN4bvc+fFljV0gAn3cSIwIfv1dhR7tGOhTGFtdjIhfd+S3RzHevGdD/xX+AE5iWwsn34dtolGfizrI5syLBch0YGMvKjz0BBtNbfDdNLRgjeRqiZkjQyURQl+A/iff5F3wNHaD6//kDT65Gx2C8apDrjt6dUX4P4BAnzRIPAxjou6GPuyYXv0+jRn4VYUY/HqQNiXR445gGwfciHj8XIDtSGo4bALeCQyGqaw=="
}

##
# Database
##

resource "aws_security_group" "scpca_portal_db" {
  name = "scpca-portal_db-${var.user}-${var.stage}"
  description = "scpca_portal_db-${var.user}-${var.stage}"
  vpc_id = aws_vpc.scpca_portal_vpc.id

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-db-${var.user}-${var.stage}"
    }
  )
}

resource "aws_security_group_rule" "scpca_portal_db_outbound" {
  type = "egress"
  from_port = 0
  to_port = 65535
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.scpca_portal_db.id
}

resource "aws_security_group_rule" "scpca_portal_db_tcp" {
  type = "ingress"
  from_port = 5432
  to_port = 5432
  protocol = "tcp"
  source_security_group_id = aws_security_group.scpca_portal_api.id
  security_group_id = aws_security_group.scpca_portal_db.id
}

##
# API
##

resource "aws_security_group" "scpca_portal_api" {
  name = "scpca-portal-api-${var.user}-${var.stage}"
  description = "scpca-portal-api-${var.user}-${var.stage}"
  vpc_id = aws_vpc.scpca_portal_vpc.id

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-api-${var.user}-${var.stage}"
    }
  )
}

resource "aws_security_group_rule" "scpca_portal_api_ssh" {
  type = "ingress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.scpca_portal_api.id
}

resource "aws_security_group_rule" "scpca_portal_api_http" {
  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.scpca_portal_api.id
}

resource "aws_security_group_rule" "scpca_portal_api_https" {
  type = "ingress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.scpca_portal_api.id
}

resource "aws_security_group_rule" "scpca_portal_api_outbound" {
  type = "egress"
  from_port = 0
  to_port = 0
  protocol = "all"
  cidr_blocks = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]
  security_group_id = aws_security_group.scpca_portal_api.id
}
