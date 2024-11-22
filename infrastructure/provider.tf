terraform {
  required_providers {
    aws = {
      source = "-/aws"
      version = "~> 5.0.0"
    }
  }
  required_version = "0.13.0"
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
