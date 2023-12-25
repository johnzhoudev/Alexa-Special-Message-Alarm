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
  sqs_queue_name = "s3-object-created-event-queue"
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

# resource "aws_s3_bucket_notification" "s3_bucket_notification" {
#   bucket = aws_s3_bucket.special_message_alarm_s3_bucket.id
#   eventbridge = true
# }

resource "aws_dynamodb_table" "special_message_alarm_dynamodb_table" {
  name           = "special-message-alarm-audio-state"
  read_capacity  = 1
  write_capacity = 1
  billing_mode = "PROVISIONED"
  hash_key = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  # NOTE: Other items defined directly on the item. Only need to define hashkey here
}

# AWS SQS Queue stuff

data "aws_iam_policy_document" "s3_object_created_event_queue_policy" {
  statement {
    effect = "Allow"

    principals {
      type = "*"
      identifiers = ["*"]
    }

    actions = ["sqs:SendMessage"]
    resources = ["arn:aws:sqs:*:*:${local.sqs_queue_name}"]

    condition {
      test = "ArnEquals"
      variable = "aws:SourceArn"
      values = [aws_s3_bucket.special_message_alarm_s3_bucket.arn]
    }
  }
}

resource "aws_sqs_queue" "s3_object_created_event_queue" {
  name = local.sqs_queue_name
  policy  = data.aws_iam_policy_document.s3_object_created_event_queue_policy.json
}

resource "aws_s3_bucket_notification" "s3_bucket_notification" {
  bucket = aws_s3_bucket.special_message_alarm_s3_bucket.id
  
  queue {
    queue_arn = aws_sqs_queue.s3_object_created_event_queue.arn
    events = ["s3:ObjectCreated:*"]
  }
}