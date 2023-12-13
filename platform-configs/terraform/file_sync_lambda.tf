data "aws_iam_policy_document" "file_sync_lambda_execution_policy" {
  statement {
    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.special_message_alarm_s3_bucket.arn
    ]
  }

  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem"
    ]

    resources = [
      aws_dynamodb_table.special_message_alarm_dynamodb_table.arn
    ]
  }

  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role_policy" "file_sync_lambda_role_policy" {
  name = "file_sync_lambda_role_policy"
  role = aws_iam_role.file_sync_lambda_execution_role.id
  policy = data.aws_iam_policy_document.file_sync_lambda_execution_policy.json
}

resource "aws_iam_role" "file_sync_lambda_execution_role" {
  name = "file_sync_lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

data "archive_file" "file_sync_lambda" {
  type = "zip"
  source_file = "./lambdas/file_sync.py"
  output_path = "./lambdas/file_sync_archive.zip"
}

resource "aws_lambda_function" "file_sync_lambda" {
  filename = "./lambdas/file_sync_archive.zip"
  function_name = "special-message-alarm-file-sync-lambda"
  role = aws_iam_role.file_sync_lambda_execution_role.arn
  handler = "file_sync.lambda_handler"

  source_code_hash = data.archive_file.file_sync_lambda.output_base64sha256

  runtime = "python3.9"

  environment {
    variables = {
      SPECIAL_MESSAGE_ALARM_TABLE_NAME = aws_dynamodb_table.special_message_alarm_dynamodb_table.id,
      AWS_REGION_NAME = local.region
    }
  }
}

resource "aws_cloudwatch_event_rule" "on_s3_file_upload" {
  name = "special_message_alarm_file_upload_event_rule"
  description = "Triggers special message alarm file sync lambda handler"

  event_pattern = jsonencode({
    source = ["aws.s3"]
    detail-type = [
        "Object Created"
    ]
    detail = {
      bucket = {
        name = [aws_s3_bucket.special_message_alarm_s3_bucket.id]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "send_to_file_sync_lambda" {
  target_id = "file_sync_lambda"
  rule = aws_cloudwatch_event_rule.on_s3_file_upload.name
  arn = aws_lambda_function.file_sync_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.file_sync_lambda.function_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.on_s3_file_upload.arn
}