resource "aws_security_group" "scpca_portal_batch" {
  name = "scpca-portal-batch-security-group-${var.user}-${var.stage}"
  vpc_id = aws_vpc.scpca_portal_vpc.id
  tags = var.default_tags

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # no ingress ssh rule because fargate does not allow server access via ssh
}

resource "aws_security_group_rule" "scpca_portal_batch_db_tcp" {
  type = "ingress"
  from_port = 5432
  to_port = 5432
  protocol = "tcp"
  source_security_group_id = aws_security_group.scpca_portal_batch.id
  security_group_id = aws_security_group.scpca_portal_db.id
}
