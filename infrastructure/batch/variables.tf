# networking
variable "scpca_portal_vpc" { default = "" }
variable "scpca_portal_subnet_1a" { default = "" }

# job_definition envars
variable "dockerhub_account" { default = "" }
variable "django_secret_key" { default = "" }
variable "database_password" { default = "" }
variable "region" { default = "" }
variable "sentry_dsn" { default = "" }
variable "scpca_portal_bucket" { default = "" }
variable "postgres_db" { default = "" }

# ec2 vars
variable "instance_type" { default = "" }
variable "ec2_key_name" { default = "" }

# security
variable "scpca_portal_db_security_group" { default = "" }

# ses
variable "ses_domain" { default = "" }

# general configuration
variable "aws_caller_identity_current" { default = "" }
variable "user" { default = "" }
variable "stage" { default = "" }
variable "batch_tags" { default = "" }
