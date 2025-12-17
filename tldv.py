from datetime import datetime
from os import system
import requests
import json

## Please install ffmpeg before running this script and make sure it's in your PATH
## brew install ffmpeg

## Please install requests before running this script
## pip3 install requests

## download video from tldv.io
##
## 1. Go to https://tldv.io/
## 2. Login
## 3. Go to the meeting you want to download
## 4. Copy the URL of the meeting
## 5. Open the developer tools (F12)
## 6. Go to the network tab
## 7. Refresh the page
## 8. Find the request to https://gw.tldv.io/v1/meetings/64145828ced74b0013d496ce/watch-page?noTranscript=true
## 9. Copy the auth token from the request headers
## 10. Run this script and paste the URL and auth token
## 11. python3 tldv.py

# Replace with your meeting URL from tldv.io
url = ""

meeting_id = url.split("/")[-1]

print("\rFound meeting ID: ", meeting_id)

# Replace with your auth token from browser developer tools
auth_token = ""

data = requests.get(
    f"https://gw.tldv.io/v1/meetings/{meeting_id}/watch-page?noTranscript=true",
    headers={
        "Authorization": auth_token,
    },
)

try:
    response = json.loads(data.text)

    meeting = response.get("meeting", {})
    name = meeting.get("name", "No name")
    createdAt = meeting.get("createdAt", datetime.now())
    source = response.get("video", {}).get("source", None)

    date = datetime.fromisoformat(createdAt.replace("Z", "+00:00"))
    normalised_date = date.strftime("%Y-%m-%d-%H-%M-%S")

    safe_name = name.replace("/", "-").replace("\\", "-")
    filename = f"{normalised_date}_{safe_name}"
    filename_ext = ".mp4"

    command = f'ffmpeg -i {source} -c copy "{filename}.{filename_ext}"'

    json_filename = f'{filename}.json'

    with open(json_filename, "w") as f:
        f.write(data.text)

    print(command)

    print("Downloading video...")

    system(command)

except Exception as e:
    print("Error encountered:", e)
    print(data.text)