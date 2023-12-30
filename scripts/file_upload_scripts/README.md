## Usage: File upload process

1. Add files you want to upload to the `assets` folder
2. In `format_file.py`, pass the `format_files` function the desired `hash_id`. Or set that id as the `HASH_AMAZON_USER_ID` env var.
3. Run `format_file.py`, and the outputted files will be in `formatted_assets`
4. Upload these files to the S3 bucket `special-message-alarm-audio-bucket`. This will automatically trigger a lambda to track the file and state in dynamo.

### To upload on s3
1. Upload the formatted file to s3, and attach metadata `max-plays` to indicate max plays and `play-immediately` if you want it to be played next.

### Dev notes
- Run `pip install -r requirements.txt` to install reqs 
- Update `requirements.txt` by running `pipreqs .`