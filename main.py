from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_audio():
    data = request.get_json()
    tiktok_url = data.get("url")

    if not tiktok_url:
        return jsonify({"error": "No URL provided"}), 400

    uid = str(uuid.uuid4())
    video_file = f"{uid}.mp4"
    audio_file = f"{uid}.mp3"

    try:
        # Download video using yt-dlp
        subprocess.run(["yt-dlp", "-o", video_file, tiktok_url], check=True)

        # Extract audio using ffmpeg
        subprocess.run(["ffmpeg", "-i", video_file, "-vn", "-acodec", "libmp3lame", audio_file], check=True)

        # Upload the audio to tmpfiles.org (anonymous)
        result = subprocess.run(["curl", "-F", f"file=@{audio_file}", "https://tmpfiles.org/api/v1/upload"], capture_output=True, text=True)
        url = result.stdout.strip()

        return jsonify({"status": "ok", "audio_url": url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup files
        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(audio_file):
            os.remove(audio_file)

app.run(host="0.0.0.0", port=8080)
