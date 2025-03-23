
from flask import Flask, request, jsonify
import os
import uuid
import yt_dlp
import subprocess
import requests

app = Flask(__name__)

@app.route("/extract", methods=["POST"])
def extract_audio():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "No URL provided"}), 400

    url = data["url"]
    video_id = str(uuid.uuid4())
    video_filename = f"{video_id}.mp4"
    mp3_filename = f"{video_id}.mp3"

    ydl_opts = {
        "format": "best",
        "outtmpl": video_filename,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return jsonify({"error": f"Video download failed: {str(e)}"}), 500

    try:
        subprocess.run([
            "ffmpeg", "-i", video_filename,
            "-vn", "-acodec", "libmp3lame",
            mp3_filename
        ], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Audio extraction failed: {str(e)}"}), 500

    try:
        with open(mp3_filename, 'rb') as f:
            upload = requests.put(f"https://transfer.sh/{mp3_filename}", data=f)
            download_url = upload.text.strip()
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500
    finally:
        if os.path.exists(video_filename):
            os.remove(video_filename)
        if os.path.exists(mp3_filename):
            os.remove(mp3_filename)

    return jsonify({"audio_url": download_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
