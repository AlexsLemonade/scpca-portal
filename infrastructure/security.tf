# This terraform file hosts the resources directly related to security.


resource "aws_key_pair" "scpca_portal" {
  key_name = "scpca-portal-key-${var.user}-${var.stage}"
  public_key = var.ssh_public_key
}

##
# Database
##

resource "aws_security_group" "scpca_portal_db" {
  name = "scpca-portal_db-${var.user}-${var.stage}"
  description = "scpca_portal_db-${var.user}-${var.stage}"
  vpc_id = aws_vpc.scpca_portal.id

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
  vpc_id = aws_vpc.scpca_portal.id

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
