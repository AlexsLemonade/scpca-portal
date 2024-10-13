variable "batch_environment" {
  type = list(object({
    name  = string
    value = string
  }))

  default = [
    for pair in flatten([for line in split("\n", templatefile("$api-configuration/environment.tpl", {
      django_secret_key  = var.django_secret_key
      database_host      = aws_db_instance.postgres_db.address
      database_port      = aws_db_instance.postgres_db.port
      database_user      = aws_db_instance.postgres_db.username
      database_password  = var.database_password
      aws_region         = var.region
      aws_s3_bucket_name = aws_s3_bucket.scpca_portal_bucket.id
      sentry_dsn         = var.sentry_dsn
      sentry_env         = var.sentry_env
    })) : split("=", line)]) :
    {
      name  = pair[0]
      value = pair[1]
    }
  ]
}

variable "batch_image" {
  type    = string
  default = "${var.dockerhub_repo}/scpca_portal_api:latest"
}

variable "batch_resource_requirements" {
  type = list(object({
    type  = string
    value = string
  }))
  # requirements match api requirements, which uses a t2.medium (2 vcpus and 4.0 GB of RAM)
  default = [
    {
      type  = "VCPU"
      value = "2.0"
    },
    {
      type  = "MEMORY"
      value = "4096"
    }
  ]
}
