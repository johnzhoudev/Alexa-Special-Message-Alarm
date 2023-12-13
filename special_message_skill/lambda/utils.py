import logging
import os
import boto3
from botocore.exceptions import ClientError
from shared_utils import *

def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('S3_PERSISTENCE_REGION'),
                             config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def get_audio(role_arn, region_name, s3_bucket, dynamo_table_name, amazon_user_id):
  # Assume creds
  sts_client = boto3.client('sts')
  assumed_role_object = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="SpecialMessageAlarmAssumeRoleSession")
  credentials = assumed_role_object['Credentials']

  # Load dynamo and get user data
  dynamodb = boto3.resource('dynamodb', 
                            aws_accesskey_id=credentials['AccessKeyId'],
                            aws_secret_access_key=credentials['SecretAccessKey'],
                            aws_session_token=credentials['SessionToken'],
                            region_name=region_name)
  
  table = dynamodb.Table(dynamo_table_name)
  user_id = hash(amazon_user_id)
  current_entry = table.get_item(Key={ "user_id": hash(user_id) })

  # No entry yet for this user_id, so create new
  if "Item" not in current_entry:
    current_entry = get_new_user_metadata(user_id)
  
  # now try and get songs
  if current_entry['']
  





