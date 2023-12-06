terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

terraform {
  backend "s3" {
    bucket                  = "terraform-backend-defuse-kit"
    key                     = "state.tfstate"
    region                  = "us-east-2"
  }
}

# VPC 
data "aws_vpc" "selected" {
  default = true
}

data "aws_subnets" "all" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

# Brass Bucket
resource "aws_s3_bucket" "brass-bucket" {
  bucket = "brass-bucket-telemetry-forza"

  tags = {
    Name        = "Project Telemetry Forza Motorsport Brass Bucket"
    Environment = "Prod"
  }
}

resource "aws_s3_bucket_public_access_block" "brass-bucket" {
  bucket = aws_s3_bucket.brass-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}