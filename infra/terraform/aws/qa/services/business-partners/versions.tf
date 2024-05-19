terraform {
  required_version = ">= 1.0.0"

  cloud {
    organization = "MisoTeam"

    workspaces {
      name = "aws-services-qa-business-partners"
    }
  }


  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}
