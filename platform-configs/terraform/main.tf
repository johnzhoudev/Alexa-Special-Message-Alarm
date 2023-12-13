terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "special-message-alarm-tfstate"
    key            = "special-message-alarm/tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "special-message-alarm-state"
  }
}

locals {
  region = "us-east-1"
}

provider "aws" {
  region = local.region
}

resource "aws_s3_bucket" "special_message_alarm_s3_bucket" {
    bucket = "special-message-alarm-audio-bucket"

    tags = {
        Name = "Special Message Alarm Audio Bucket"
    }
}

resource "aws_s3_bucket_notification" "s3_bucket_notification" {
  bucket = aws_s3_bucket.special_message_alarm_s3_bucket.id
  eventbridge = true
}

resource "aws_dynamodb_table" "special_message_alarm_dynamodb_table" {
  name           = "special-message-alarm-audio-state"
  read_capacity  = 1
  write_capacity = 1
  billing_mode = "PROVISIONED"
  hash_key = "userid"

  attribute {
    name = "userid"
    type = "S"
  }

  # NOTE: Other items defined directly on the item. Only need to define hashkey here
}