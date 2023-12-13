## Usage: File upload process

1. Add files you want to upload to the `assets` folder
2. In `format_file.py`, pass the `format_files` function the desired amazon id. Or set that id as the `AMAZON_USER_ID` env var.
3. Run `format_file.py`, and the outputted files will be in `formatted_assets`
4. Upload these files to the S3 bucket `special-message-alarm-audio-bucket`. This will automatically trigger a lambda to track the file and state in dynamo.

