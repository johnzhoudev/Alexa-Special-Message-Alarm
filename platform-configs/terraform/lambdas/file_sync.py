import boto3
import os
from shared_utils import *

def lambda_handler(event, context):
  print("Received event: ", event)

  region_name = os.getenv('AWS_REGION_NAME')
  if (region_name is None):
    raise RuntimeError("Error, AWS_REGION_NAME env var is null")
  table_name = os.getenv('SPECIAL_MESSAGE_ALARM_TABLE_NAME')
  if (table_name is None):
    raise RuntimeError("Error, SPECIAL_MESSAGE_ALARM_TABLE_NAME env var is null")

  dynamodb_client = boto3.resource('dynamodb', region_name=region_name)
  table = dynamodb_client.Table(table_name)

  # Get each hash id from dynamo
  response = table.scan(AttributesToGet=[
    "user_id"
  ])

  if "Items" not in response:
    print("Error, no items in dynamo found.")
    return {
      "event": event,
      "status": "Error",
      "msg": "No items in dynamo found during scan."
    }

  for item in response['Items']:
    user_id = item['user_id']
    sync_files_for_user_hash(user_id, table)

  return {
    "event": event,
    "status": "Success"
  }

def sync_files_for_user_hash(user_id, dynamo_table):
  MAX_KEYS = 1000
  s3_client, s3_bucket_name = get_s3_client_and_bucket_name()
  
  # Get dynamo entry
  current_entry = dynamo_table.get_item(Key={ "user_id": user_id })
  print("Got item", current_entry)
  if "Item" not in current_entry:
    current_entry = get_new_user_metadata(user_id)
  else:
    current_entry = current_entry["Item"]
  
  # Build tracked sets
  tracked_items = set()
  for item in current_entry['unplayed'] + current_entry['played'] + current_entry['unplayed_play_immediately']:
    tracked_items.add(item["file_name"])
  
  # Get all files for user user_id
  response = s3_client.list_objects_v2(
    Bucket=s3_bucket_name,
    Prefix=user_id,
    MaxKeys=MAX_KEYS
  )

  if "Contents" not in response:
    print(f"No results found for user user_id {user_id}")
    return
  
  if len(response["Contents"]) == MAX_KEYS:
    print("WARNING: Max keys reached for user " + user_id)
  
  for item in response['Contents']:
    file_name = item['Key']
    print("Processing " + file_name)

    if get_s3_should_delete(file_name):
      print("Deleting " + file_name)
      s3_delete_file(file_name)
      remove_audio(file_name, current_entry)
    elif file_name not in tracked_items:
      print("Adding " + file_name)
      add_audio(file_name, current_entry)
        
  current_entry['last_updated_at'] = get_current_date_time()
  res = dynamo_table.put_item(Item=current_entry)
  print("Put Item response:", res)
  return res

# Helpers
def get_s3_client_and_bucket_name():
  s3_client = boto3.client("s3")
  bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
  if (bucket_name is None):
    raise RuntimeError("Error, AWS_S3_BUCKET_NAME env var is null")
  
  return s3_client, bucket_name

def s3_delete_file(file_name):
  s3_client, bucket_name = get_s3_client_and_bucket_name()
  return s3_client.delete_object(Bucket=bucket_name, Key=file_name)

def get_s3_should_delete(file_name):
  s3, bucket_name = get_s3_client_and_bucket_name()
  SHOULD_DELETE_TAG = "shouldDelete"

  try:
    response = s3.get_object_tagging(Bucket=bucket_name, Key=file_name)
    tags = {}
    for tag in response["TagSet"]:
      tags[tag["Key"]] = tag["Value"]
    print("Got tags for file", tags)
    return tags[SHOULD_DELETE_TAG] == "true" if SHOULD_DELETE_TAG in tags else False
  except Exception as e:
    print("Error getting file tags for file", file_name)
    print(e)
    raise RuntimeError("Error getting file tags")

# Returns max plays, play immediately
def get_s3_file_metadata(file_name):
  MAX_PLAYS_METADATA_KEY = os.getenv("MAX_PLAYS_METADATA_KEY", default="max-plays")
  PLAY_IMMEDIATELY_METADATA_KEY = os.getenv("PLAY_IMMEDIATELY_METADATA_KEY", default="play-immediately")

  s3, bucket_name = get_s3_client_and_bucket_name()

  try:
    response = s3.head_object(Bucket=bucket_name, Key=file_name)
    print("Got metadata for file", response)
    response = response["Metadata"]
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

def remove_audio(file_name, current_entry):
  current_entry['unplayed'] = [entry for entry in current_entry['unplayed'] if entry['file_name'] != file_name]
  current_entry['unplayed_play_immediately'] = [entry for entry in current_entry['unplayed_play_immediately'] if entry['file_name'] != file_name]
  current_entry['played'] = [entry for entry in current_entry['played'] if entry['file_name'] != file_name]
  print("removed", file_name)

def build_file_metadata(file_name, max_plays=None):
  return {
    "num_plays": 0,
    "max_plays": max_plays,
    "file_name": file_name
  }
