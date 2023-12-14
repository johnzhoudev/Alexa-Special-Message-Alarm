data "aws_iam_policy_document" "special_message_alarm_lambda_execution_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:PutObjectTagging"
    ]

    resources = [
      "${aws_s3_bucket.special_message_alarm_s3_bucket.arn}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem"
    ]

    resources = [
      aws_dynamodb_table.special_message_alarm_dynamodb_table.arn
    ]
  }
}

resource "aws_iam_role_policy" "special_message_alarm_lambda_role_policy" {
  name = "special_message_alarm_lambda_role_policy"
  role = aws_iam_role.special_message_alarm_lambda_execution_role.id
  policy = data.aws_iam_policy_document.special_message_alarm_lambda_execution_policy.json
}

resource "aws_iam_role" "special_message_alarm_lambda_execution_role" {
  name = "special_message_alarm_lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = "arn:aws:iam::693357513899:role/AlexaHostedSkillLambdaRole"
        }
      },
    ]
  })
}
