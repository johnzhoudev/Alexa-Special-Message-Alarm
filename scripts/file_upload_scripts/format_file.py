## Run from file_upload_scripts directory
import os

from pydub import AudioSegment, effects
from moviepy.video.io.VideoFileClip import VideoFileClip
from dotenv import load_dotenv

load_dotenv()

ASSETS_PATH_BASE = "assets"
FORMATTED_ASSETS_PATH = "formatted_assets"
HASH_USER_ID_ENV_VAR = "HASH_AMAZON_USER_ID"

def format_files(hash_id=None):

  if hash_id is None:
    hash_id = os.getenv(HASH_USER_ID_ENV_VAR)

  assets_path = os.path.join(ASSETS_PATH_BASE, hash_id)
  files = os.listdir(assets_path)

  for file_name in files:
    if (".DS_Store" in file_name): continue

    file_path = os.path.join(assets_path, file_name)

    print("Processing", file_path)

    # Convert to mp3
    if file_path.endswith(".mp4"):
      print("Converting to mp3")
      video_clip = VideoFileClip(file_path)
      audio_clip = video_clip.audio
      file_path = file_path.strip(".mp4")
      audio_clip.write_audiofile(file_path + ".mp3", codec='mp3')
      os.remove(file_path + ".mp4")
      # Modify so rest of function can use correct names
      file_path += ".mp3"
      file_name = file_name.strip(".mp4") + ".mp3"

    print("file path", file_path)
    # Normalize audio volume
    raw_sound = AudioSegment.from_file(f"./{file_path}")
    normalized_sound = effects.normalize(raw_sound)

    asset_path = os.path.join(FORMATTED_ASSETS_PATH, hash_id)
    if not os.path.exists(asset_path):
      os.mkdir(asset_path)
    normalized_sound.export(os.path.join(FORMATTED_ASSETS_PATH, hash_id, file_name))

if __name__ == "__main__":
  format_files()
