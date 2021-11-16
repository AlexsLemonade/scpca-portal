# This terraform file hosts the resources directly related to security.


resource "aws_key_pair" "scpca_portal" {
  key_name = "scpca-portal-key-${var.user}-${var.stage}"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC9UVCjK3S2BtKLnJZ8ASizBkiLluccJ8O0CDB6OZ9tHIN2pXnXS/j11azvxpoJKlXEohXbTj/1DLnpF4LSyEDkt+2cEQA5Oa646mlud/axIDepJkuxf/0+/0JFJW5eAGmQ2qxUeouSZeWwc9pdFQMblkNZnFZ5qxSsU+GXoWUdGLuwjXCmql9d7TJl3NlSNmmfmgffpQXM4YxWgD/uUyAGrynyb1Bi314220emo1E5caLPG0Pz7r1dmUc+fseEjNaj4M/pPS82XgHXrFyEfJqO0p8FfXC129s4+CgRYB+xdpiZdRtccKBmmBH08uSkQ3hDV2Z0EyD5onCnzqiVZ3AkSxNAKkxHte53Kf0JRX0DBk0VLoJK/vFVKFIwpzW1mGku0qcA+FOk8eMsyefN/mi0QsBeq0tR7LNS7TdsRqd4dVEuh4GphFkm5MHFGQUs1DQktb1nkZcGyraQQJKX1cAsiWNg9P3YfxtS4NTPBX5HgYZTF1pTEq4nJZbtXawNYdm0jiqAYS+A76UToeRUUPngow173Nzf8Bc8KTSgNeoV+0J1wxGh4O2z83xR8GTiFxGJhHLPTr2s8PtaAOybBmSxm4pUfsUzyi/uZoP4dCBuqgVRcemctSZ8zNgBGo12Q6ZdvwGEwUJ++eVFVBk+UmcW591Doa2pGNbj2WBbx3zxxQ=="
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
