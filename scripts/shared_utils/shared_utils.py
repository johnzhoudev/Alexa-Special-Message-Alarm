import hashlib
from datetime import datetime

## NOTE: Update from scripts/shared_utils, and share using shared_utils_distribute.py!

def hash(text):
  return hashlib.sha1(text.encode('ascii')).hexdigest()

def get_current_date_time():
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

