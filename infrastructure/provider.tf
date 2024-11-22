terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0.0"
    }
  }
  required_version = "1.0.8"
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
