# This terraform file hosts the resources directly related to the
# postgres RDS instance.

# Currently exists, will be deleted after aws_db_parameter_group.postgres_parameters is in use.
resource "aws_db_parameter_group" "postgres_parameters" {
  name = "postgres-parameters-${var.user}-${var.stage}"
  description = "Postgres Parameters ${var.user} ${var.stage}"
  family = "postgres9.6"

  parameter {
    name = "deadlock_timeout"
    value = "60000" # 60000ms = 60s
  }

  parameter {
    name = "statement_timeout"
    value = "60000" # 60000ms = 60s
  }
}

resource "aws_db_parameter_group" "postgres_parameters" {
  name = "scpca-portal-postgres-parameters-${var.user}-${var.stage}"
  description = "Postgres Parameters ${var.user} ${var.stage}"
  family = "postgres9.6"

  parameter {
    name = "deadlock_timeout"
    value = "60000" # 60000ms = 60s
  }

  parameter {
    name = "statement_timeout"
    value = "60000" # 60000ms = 60s
  }

  tags = var.default_tags
}

resource "aws_db_instance" "postgres_db" {
  identifier = "scpca-portal-${var.user}-${var.stage}"
  allocated_storage = 100
  storage_type = "gp2"
  engine = "postgres"
  engine_version = "9.6.11"
  auto_minor_version_upgrade = false
  instance_class = var.database_instance_type
  name = "scpca_portal"
  port = "5432"
  username = "scpcapostgresuser"
  password = var.database_password

  db_subnet_group_name = aws_db_subnet_group.scpca_portal.name
  parameter_group_name = aws_db_parameter_group.postgres_parameters.name

  # TF is broken, but we do want this protection in prod.
  # Related: https://github.com/hashicorp/terraform/issues/5417
  # Only the prod's bucket prefix is empty.
  skip_final_snapshot = var.stage == "prod" ? false : true
  final_snapshot_identifier = var.stage == "prod" ? "scpca-portal-prod-snapshot" : "none"

  vpc_security_group_ids = [aws_security_group.scpca_portal_db.id]
  multi_az = true
  publicly_accessible = true

  backup_retention_period  = var.stage == "prod" ? "7" : "0"

  tags = var.default_tags
}
