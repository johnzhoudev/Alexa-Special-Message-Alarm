import logging
import boto3
from botocore.exceptions import ClientError
from shared_utils import *
import random
from ask_sdk_core.handler_input import HandlerInput

# Consts
NO_FILES_UPLOADED = "No files uploaded"

def get_amazon_user_id(handler_input):
  # type: (HandlerInput) -> str
  return handler_input.request_envelope.context.system.user.user_id

def get_audio(role_arn, region_name, s3_bucket, dynamo_table_name, amazon_user_id):
  # Assume creds
  sts_client = boto3.client('sts')
  assumed_role_object = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="SpecialMessageAlarmAssumeRoleSession", DurationSeconds=900)
  credentials = assumed_role_object['Credentials']

  # Load s3
  s3_client = boto3.resource('s3', 
                          aws_access_key_id=credentials['AccessKeyId'],
                          aws_secret_access_key=credentials['SecretAccessKey'],
                          aws_session_token=credentials['SessionToken'],
                          region_name=region_name,
                          config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
  s3_client = s3_client.meta.client

  # Load dynamo and get user data
  dynamodb = boto3.resource('dynamodb', 
                            aws_access_key_id=credentials['AccessKeyId'],
                            aws_secret_access_key=credentials['SecretAccessKey'],
                            aws_session_token=credentials['SessionToken'],
                            region_name=region_name)
  
  table = dynamodb.Table(dynamo_table_name)
  user_id = hash(amazon_user_id)
  current_entry = table.get_item(Key={ "user_id": user_id })

  # No entry yet for this user_id, so create new
  if "Item" not in current_entry:
    current_entry = get_new_user_metadata(user_id)
    # create new entry in dynamo
    put_current_entry(current_entry, table)
  else:
    current_entry = current_entry['Item']
  print("Got entry", current_entry)
  
  # Now try and get songs
  if len(current_entry['unplayed_play_immediately']) > 0:
    audio_entry = current_entry['unplayed_play_immediately'][0]
  elif len(current_entry['unplayed']) > 0:
    audio_entry = random.choice(current_entry['unplayed'])
  else: # if no songs available, means no songs uploaded, so return None
    print("No files available")
    return NO_FILES_UPLOADED, None

  print("Chosen", audio_entry)
  played_entry_update_state(audio_entry, current_entry, table, s3_client, s3_bucket)

  # if now no more possible played songs, transfer played to unplayed
  print(current_entry)
  if len(current_entry['unplayed_play_immediately']) == 0 and len(current_entry['unplayed']) == 0:
    print("No more audio to play, refilling from played")
    current_entry['unplayed'] = current_entry['played']
    current_entry['played'] = []
    print("Unplayed:", current_entry['unplayed'])
    print("Played:", current_entry['played'])
  
  print("Writing back entry:", current_entry)
  put_current_entry(current_entry, table)

  try:
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': s3_bucket, 'Key': audio_entry['file_name']}, ExpiresIn=900)
  except ClientError as e:
    print("Failed to generate url for:", audio_entry)
    logging.error(e)
    return None, None
  print("Returning:", audio_entry)

  return url, audio_entry['file_name']
  
def put_current_entry(current_entry, table):
  current_entry['last_updated_at'] = get_current_date_time()
  put_current_entry(current_entry, table)

def played_entry_update_state(audio_entry, current_entry, dynamo_table, s3_client, s3_bucket):
  audio_entry['num_plays'] += 1

  # if reached max plays, delete from everywhere
  if (audio_entry['max_plays'] and audio_entry['num_plays'] >= audio_entry['max_plays']):
    print("Max plays reached for entry", audio_entry)
    delete_from_aws(audio_entry, dynamo_table, s3_client, s3_bucket)
    return

  move_audio_entry_to_played(audio_entry, current_entry)

def delete_from_aws(audio_entry, current_entry, dynamo_table, s3_client, s3_bucket):
  try:
    delete_audio_entry_from_unplayed(audio_entry, current_entry)
    put_current_entry(current_entry, dynamo_table)
    s3_client.delete_object(Bucket=s3_bucket, Key=audio_entry['file_name'])
  except Exception as e:
    print("Error deleting audio_entry", e)
    print("audio_entry", audio_entry)
  else:
    print("Successfully deleted audio entry", audio_entry)

def delete_audio_entry_from_unplayed(audio_entry, current_entry):
  current_entry['unplayed'] = [entry for entry in current_entry['unplayed'] if entry['file_name'] != audio_entry['file_name']]
  current_entry['unplayed_play_immediately'] = [entry for entry in current_entry['unplayed_play_immediately'] if entry['file_name'] != audio_entry['file_name']]

def move_audio_entry_to_played(audio_entry, current_entry):
  delete_audio_entry_from_unplayed(audio_entry, current_entry)
  current_entry['played'].append(audio_entry)