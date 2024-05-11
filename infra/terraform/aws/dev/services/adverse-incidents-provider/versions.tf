terraform {
  required_version = ">= 1.0.0"

  cloud {
    organization = "MisoTeam"

    workspaces {
      name = "aws-services-dev-adverse-incidents-provider"
    }
  }


  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}
