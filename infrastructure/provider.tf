terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.76.1"

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
