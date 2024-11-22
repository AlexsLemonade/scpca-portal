# TODO: remove comments when version upgraded
# terraform {
#   required_providers {
#     aws = {
#      source = "hashicorp/aws"
#      version = "3.37.0"
#    }
#  }
#}


provider "aws" {
  region  = var.region
  version = ">= 3.37.0, < 4.0.0"

  default_tags {
    tags = {
      team    = "engineering"
      project = "ScPCA Portal"
    }
  }
}
