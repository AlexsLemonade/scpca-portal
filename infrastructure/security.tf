# This terraform file hosts the resources directly related to security.


resource "aws_key_pair" "scpca_portal" {
  key_name = "scpca-portal-key-${var.user}-${var.stage}"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDBdLoGqW+z1lc8KiNWg5OOyHjce/ulev8Xh8qK0FKVtIGNMt55pKXpFW8Wjc7e3PP4omq5lIJvkHOQYvTNE1xlzRSCzsNJTjyPVwBLDUek/cXqJUP3HqZ+XsZnoMC6yDKzbCec6e9XpJJGLiHB5L/80+J7sGsDYAcqsitf3WbNIZbqCPC3w8unx35UDNIvD1Ow4pK5VTvhEVnGsy9dKBe5ClXxxOl5WC2sPpVDRdbYjMnc/xXuIRlDd7F1J9zxjjERO76/Ll8AhwRkWAokOMA1JEh2xYmij/HFbWi2aQ5DWMpaW4QkH34wbfTUtVe6dLdyAwpwakx4lJnboiCzbPsAy3Mrzmok/jNze64Ub6B/GPnuDuB/7efIvBoZhaV984Gi5T9JqMdfPMXtIUGgrq1JH/zUsPOzcrPtHpMa2zLumysEiexmb6RpVkwd7qKlHjLKieWfeLkP4iJfL2Ta+T3TqtVJ1tCPviY2gIC0pFl+iyUPgmMKKrber2b187OBqn7sZNLipO+6F8Yz86f1FmoSpny5DqAIRyDCVtjJdkIF+hXd3dvWNv4OgGttIVyYAN1Lem51czSXse04Fca3hedaTWj6k7GF48FdmqjEpaj0ZOKArkgQJ4uiKds8DLmZrHidd3kS8+3cSMyJDodHUW1UbqvfpucYADGdmHrLrGJWAQ=="
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
