provider "aws" {
  version = "5.12.0"
  region  = var.region

  default_tags {
    tags = {
      team    = "engineering"
      project = "ScPCA Portal"
    }
  }
}
