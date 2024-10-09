provider "aws" {
  version = "3.37.0"
  region  = var.region

  default_tags {
    tags = {
      team    = "engineering"
      project = "ScPCA Portal"
    }
  }
}
