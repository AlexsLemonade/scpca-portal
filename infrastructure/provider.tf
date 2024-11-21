terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.0.0"

    }
  }
}


provider "aws" {
  region  = var.region

  default_tags {
    tags = {
      team    = "engineering"
      project = "ScPCA Portal"
    }
  }
}
