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

data "aws_caller_identity" "current" {}

locals {
  aws_account_id                   = data.aws_caller_identity.current.account_id
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

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.brass-bucket.id

  queue {
    queue_arn     = aws_sqs_queue.forza_records_queue.arn
    events        = ["s3:ObjectCreated:*"]
  }

  depends_on = [ aws_sqs_queue.forza_records_queue,
    aws_sqs_queue_policy.forza_sqs_queue_policy ]
}

# SQS 
resource "aws_sqs_queue" "forza_records_queue" {
  name                       = "track_records_s3"
  delay_seconds              = 10
  max_message_size           = 2048
  message_retention_seconds  = 1000
  visibility_timeout_seconds = 60
  receive_wait_time_seconds  = 10

  tags = {
    Environment = "production"
  }
}

resource "aws_sqs_queue_policy" "forza_sqs_queue_policy" {
  queue_url = aws_sqs_queue.forza_records_queue.id
  policy    = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Sid": "__default_statement_ID",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "SQS:SendMessage",
      "Resource": "${aws_sqs_queue.forza_records_queue.arn}",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "${local.aws_account_id}"
        },
        "ArnLike": {
          "aws:SourceArn": "${aws_s3_bucket.brass-bucket.arn}"
        }
      }
    }
  ]
}
POLICY
}