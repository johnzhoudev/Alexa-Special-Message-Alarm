## Run from file_upload_scripts directory
import os

from pydub import AudioSegment, effects

ASSETS_PATH = "assets"
FORMATTED_ASSETS_PATH = "formatted_assets"
HASH_USER_ID_ENV_VAR = "HASH_AMAZON_USER_ID"

def format_files(hash_id=None):

  if hash_id is None:
    hash_id = os.getenv(HASH_USER_ID_ENV_VAR)

  files = os.listdir(ASSETS_PATH)

  for file_name in files:
    file_path = os.path.join(ASSETS_PATH, file_name)

    # Normalize audio volume
    print("Processing", file_path)
    raw_sound = AudioSegment.from_file(f"./{file_path}")
    normalized_sound = effects.normalize(raw_sound)

    new_file_name = f"{hash_id}-{file_name}"
    asset_path = os.path.join(FORMATTED_ASSETS_PATH, hash_id)
    if not os.path.exists(asset_path):
      os.mkdir(asset_path)
    normalized_sound.export(os.path.join(FORMATTED_ASSETS_PATH, hash_id, new_file_name))

if __name__ == "__main__":
  format_files("")
