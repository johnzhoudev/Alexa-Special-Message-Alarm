## Run from file_upload_scripts directory
import os
import shutil
import hashlib

ASSETS_PATH = "assets"
FORMATTED_ASSETS_PATH = "formatted_assets"
AMAZON_USER_ID_ENV_VAR = "AMAZON_USER_ID"


def format_files(amazon_user_id=None):

  if amazon_user_id is None:
    amazon_user_id = os.getenv(AMAZON_USER_ID_ENV_VAR)

  files = os.listdir(ASSETS_PATH)

  for file_name in files:
    file_path = os.path.join(ASSETS_PATH, file_name)

    # TODO: Process audio files

    new_file_name = f"{hash(amazon_user_id)}-{file_name}"
    shutil.copy(file_path, os.path.join(FORMATTED_ASSETS_PATH, new_file_name))

def hash(text):
  return hashlib.sha1(text.encode('ascii')).hexdigest()

if __name__ == "__main__":
  format_files()
