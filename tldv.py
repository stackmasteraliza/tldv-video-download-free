from datetime import datetime
from os import system
import requests
import json

# Replace with your meeting URL from tldv.io
url = "https://tldv.io/app/meetings/YOUR_MEETING_ID_HERE"

meeting_id = url.split("/")[-1]

print("\rFound meeting ID: ", meeting_id)

# Replace with your auth token from browser developer tools
auth_token = "Bearer YOUR_AUTH_TOKEN_HERE"

data = requests.get(
    f"https://gw.tldv.io/v1/meetings/{meeting_id}/watch-page",
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

    # Extract and save transcript
    transcript_data = response.get("video", {}).get("transcript", {}).get("data", [])

    if transcript_data:
        transcript_filename = f'{filename}_transcript.txt'
        with open(transcript_filename, "w", encoding="utf-8") as f:
            for segment in transcript_data:
                if not segment:
                    continue
                # Get speaker and timestamp from first word in segment
                first_word = segment[0]
                speaker = first_word.get("speaker", "Unknown")
                start_time = first_word.get("startTime", {})
                seconds_total = int(start_time.get("seconds", 0))

                # Convert to mm:ss format
                minutes = seconds_total // 60
                seconds = seconds_total % 60
                timestamp = f"{minutes:02d}:{seconds:02d}"

                # Combine all words in segment
                text = " ".join(word.get("word", "") for word in segment)

                f.write(f"[{timestamp}] {speaker}: {text}\n")

        print(f"Transcript saved to: {transcript_filename}")
    else:
        print("No transcript available for this meeting")

    print(command)

    print("Downloading video...")

    system(command)

except Exception as e:
    print("Error encountered:", e)
    print(data.text)