import boto3
import os
from shared_utils import *

def lambda_handler(event, context):
  print("Received event: ", event)

  for record in event["Records"]:
    if (record["body"][""])


  file_name = event['detail']['object']['key']
  user_id = file_name.split("-")[0]
  print("User Id:", user_id)

  region_name = os.getenv('AWS_REGION_NAME')
  if (region_name is None):
    raise RuntimeError("Error, AWS_REGION_NAME env var is null")
  table_name = os.getenv('SPECIAL_MESSAGE_ALARM_TABLE_NAME')
  if (table_name is None):
    raise RuntimeError("Error, SPECIAL_MESSAGE_ALARM_TABLE_NAME env var is null")

  # check if exists in dynamo, else create new entry
  dynamodb_client = boto3.resource('dynamodb', region_name=region_name)
  table = dynamodb_client.Table(table_name)

  current_entry = table.get_item(Key={ "user_id": user_id })
  print("Got item", current_entry)

  if "Item" not in current_entry:
    current_entry = get_new_user_metadata(user_id)
  else:
    current_entry = current_entry["Item"]

  # always filter out and overwrite
  # If file was in played, overwrite and add to unplayed or unplayed_play_immediately
  remove_audio(file_name, current_entry)
  add_audio(file_name, current_entry)

  current_entry['last_updated_at'] = get_current_date_time()
  res = table.put_item(Item=current_entry)
  print("Put Item response:", res)
  
  return {
    "event": event,
    "status": "Success"
  }

# Helpers

def remove_audio(file_name, current_entry):
  current_entry['unplayed'] = [entry for entry in current_entry['unplayed'] if entry['file_name'] != file_name]
  current_entry['unplayed_play_immediately'] = [entry for entry in current_entry['unplayed_play_immediately'] if entry['file_name'] != file_name]
  current_entry['played'] = [entry for entry in current_entry['played'] if entry['file_name'] != file_name]
  print("removed", file_name)

# Returns max plays, play immediately
def get_s3_file_metadata(file_name):
  MAX_PLAYS_METADATA_KEY = os.getenv("MAX_PLAYS_METADATA_KEY", default="max-plays")
  PLAY_IMMEDIATELY_METADATA_KEY = os.getenv("PLAY_IMMEDIATELY_METADATA_KEY", default="play-immediately")

  s3 = boto3.client("s3")
  bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
  if (bucket_name is None):
    raise RuntimeError("Error, AWS_S3_BUCKET_NAME env var is null")

  try:
    response = s3.head_object(Bucket=bucket_name, Key=file_name)["Metadata"]
    print("Got metadata for file", response)
    max_plays = int(response[MAX_PLAYS_METADATA_KEY]) if MAX_PLAYS_METADATA_KEY in response else None
    play_immediately = response[PLAY_IMMEDIATELY_METADATA_KEY] == "true" if PLAY_IMMEDIATELY_METADATA_KEY in response else False
    return max_plays, play_immediately
  except Exception as e:
    print("Error getting file metadata for file", file_name)
    print(e)
    raise RuntimeError("Error getting file metadata")

def add_audio(file_name, current_entry):
  max_plays, play_immediately = get_s3_file_metadata(file_name)
  metadata = build_file_metadata(file_name, max_plays=max_plays)
  if play_immediately:
    current_entry['unplayed_play_immediately'].insert(0, metadata)
    print("Added to unplayed_play_immediately", file_name)
  else:
    print("Added to unplayed", file_name)
    current_entry['unplayed'].append(metadata)

def build_file_metadata(file_name, max_plays=None):
  return {
    "num_plays": 0,
    "max_plays": max_plays,
    "file_name": file_name
  }
