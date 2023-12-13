import boto3
import os
import hashlib
from datetime import datetime

def lambda_handler(event, context):
  print("Received event: ", event)
  file_name = event['detail']['object']['key']
  user_id = file_name.split("-")[0]
  print("User Id:", user_id)

  # region_name = os.environ['REGION_NAME']
  # get all env variables
  region_name = "us-east-1"
  # table_name = os.environ['TABLE_NAME']
  table_name = "special-message-alarm-audio-state"

  # check if exists in dynamo, else create new entry
  dynamodb_client = boto3.resource('dynamodb', region_name=region_name)
  table = dynamodb_client.Table(table_name)

  current_entry = table.get_item(Key={ "userid": user_id })

  if "Item" not in current_entry:
    current_entry = {
      "userid": user_id,
      "unplayed": [],
      "played": [],
      "unplayed_play_immediately": [],
      "created_at": get_current_date_time(),
      "last_updated_at": get_current_date_time()
    }
  else:
    current_entry = current_entry["Item"]

  # if song already exists, skip
  if (any(metadata['file_name'] == file_name for metadata in current_entry['unplayed'])):
    print("File already exists")
    return {
      "event": event,
      "status": "File already exists"
    }

  current_entry['unplayed'].append(build_file_metadata(file_name))
  current_entry['last_updated_at'] = get_current_date_time()
  res = table.put_item(Item=current_entry)
  print("Put Item response:", res)
  
  return {
    "event": event,
    "status": "Success"
  }

# Helpers

def build_file_metadata(file_name, max_plays=None):
  return {
    "num_plays": 0,
    "max_plays": max_plays,
    "file_name": file_name
  }

def get_current_date_time():
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 