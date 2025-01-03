# Alexa Special Message Alarm

Christmas present for a close friend, this repo sets up AWS resources and an alexa skill that can be used to play custom voice messages as alarms. This skill can then be invoked by setting an alexa routine at any time, effectively becoming an alarm.

## How It Works
1. Audio is uploaded manually to an `S3` bucket prefixed by that user's amazon alexa ID
![image](https://github.com/johnzhoudev/Alexa-Special-Message-Alarm/assets/52118413/7d89657f-38e6-4aa5-a7aa-f3b63ef76ae1)
2. A Lambda runs to create metadata for each audio clip in `DynamoDB` tracking `numPlays` and `maxPlays`
![image](https://github.com/johnzhoudev/Alexa-Special-Message-Alarm/assets/52118413/526723af-9770-49d6-8a76-cb18379a3ce2)
3. An alexa routine is set for a specific time and activates the `Special Message Alarm` skill, which triggers a lambda that uses the `DynamoDB` / `S3` entries to select a random clip and play it as an alarm.
