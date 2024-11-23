# The configuration contained in this file specifies AWS resources
# related to networking.

resource "aws_vpc" "scpca_portal_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "scpca-portal-${var.user}-${var.stage}"
  }
}

resource "aws_subnet" "scpca_portal_1a" {
  availability_zone = "${var.region}a"
  cidr_block = "10.0.0.0/17"
  vpc_id = aws_vpc.scpca_portal_vpc.id
  map_public_ip_on_launch = true

  tags = {
    Name = "scpca-portal-1a-${var.user}-${var.stage}"
  }
}

resource "aws_subnet" "scpca_portal_1b" {
  availability_zone = "${var.region}b"
  cidr_block = "10.0.128.0/17"
  vpc_id = aws_vpc.scpca_portal_vpc.id

  map_public_ip_on_launch = true

  tags = {
    Name = "scpca-portal-1b-${var.user}-${var.stage}"
  }
}

resource "aws_internet_gateway" "scpca_portal" {
  vpc_id = aws_vpc.scpca_portal_vpc.id

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-${var.user}-${var.stage}"
    }
  )
}

# Allow access for ssh.
resource "aws_route_table" "scpca_portal" {
  vpc_id = aws_vpc.scpca_portal_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.scpca_portal.id
  }

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-portal-${var.user}-${var.stage}"
    }
  )
}

resource "aws_route_table_association" "scpca_portal_1a" {
  subnet_id = aws_subnet.scpca_portal_1a.id
  route_table_id = aws_route_table.scpca_portal.id
}

resource "aws_route_table_association" "scpca_portal_1b" {
  subnet_id = aws_subnet.scpca_portal_1b.id
  route_table_id = aws_route_table.scpca_portal.id
}

resource "aws_db_subnet_group" "scpca_portal" {
  name = "scpca-portal-${var.user}-${var.stage}"
  subnet_ids = [aws_subnet.scpca_portal_1a.id, aws_subnet.scpca_portal_1b.id]

  tags = merge(
    var.default_tags,
    {
      Name = "ScPCA Portal DB Subnet ${var.user}-${var.stage}"
    }
  )
}

# Get the API a static IP address.
resource "aws_eip" "scpca_portal_api_ip" {
  domain = "vpc"

  tags = merge(
    var.default_tags,
    {
      Name = "ScPCA Portal API Elastic IP ${var.user}-${var.stage}"
    }
  )
}

output "elastic_ip_address" {
  value = aws_eip.scpca_portal_api_ip.public_ip
}


# As per https://aws.amazon.com/elasticloadbalancing/details/:
#
# You can select the appropriate load balancer based on your
# application needs. If you need flexible application management, we
# recommend that you use an Application Load Balancer. If extreme
# performance and static IP is needed for your application, we
# recommend that you use a Network Load Balancer. If you have an
# existing application that was built within the EC2-Classic network,
# then you should use a Classic Load Balancer.
#
# it appears an Network Load Balancer would be best for us because we
# need a static IP address to point DNS to.
resource "aws_lb" "scpca_portal_api_load_balancer" {
  # Keep it short because there is a 32 char limit on this name
  name = "scpca-api-${var.user}-${var.stage}"
  internal = false
  load_balancer_type = "network"

  # Only one subnet is allowed and the API lives in 1a.
  subnet_mapping {
    subnet_id = aws_subnet.scpca_portal_1a.id
    allocation_id = aws_eip.scpca_portal_api_ip.id
  }
}

resource "aws_lb_target_group" "api-http" {
  port = 80
  protocol = "TCP"
  vpc_id = aws_vpc.scpca_portal_vpc.id
  stickiness {
    enabled = false
    type = "source_ip"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-api-${var.user}-${var.stage}-http"
    }
  )
}

resource "aws_lb_listener" "api-http" {
  load_balancer_arn = aws_lb.scpca_portal_api_load_balancer.arn
  protocol = "TCP"
  port = 80

  default_action {
    target_group_arn = aws_lb_target_group.api-http.arn
    type = "forward"
  }
}

resource "aws_lb_target_group_attachment" "api-http" {
  target_group_arn = aws_lb_target_group.api-http.arn
  target_id = aws_instance.api_server_1.id
  port = 80
}

resource "aws_lb_target_group" "api-https" {
  port = 443
  protocol = "TCP"
  vpc_id = aws_vpc.scpca_portal_vpc.id
  stickiness {
    enabled = false
    type = "source_ip"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(
    var.default_tags,
    {
      Name = "scpca-api-${var.user}-${var.stage}-https"
    }
  )
}

resource "aws_lb_listener" "api-https" {
  load_balancer_arn = aws_lb.scpca_portal_api_load_balancer.arn
  protocol = "TCP"
  port = 443

  default_action {
    target_group_arn = aws_lb_target_group.api-https.arn
    type = "forward"
  }
}

resource "aws_lb_target_group_attachment" "api-https" {
  target_group_arn = aws_lb_target_group.api-https.arn
  target_id = aws_instance.api_server_1.id
  port = 443
}
